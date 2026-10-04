"""Cross-platform persistence for local game statistics."""

from __future__ import annotations

import json
from typing import Any, Protocol

import flet as ft

DIFFICULTIES = ("Easy", "Medium", "Hard", "Expert")
STATISTICS_KEY = "com.mightyalok00.sudoku_flow.statistics.v1"


class Preferences(Protocol):
    """Minimal interface used by the Flet preferences service."""

    async def get(self, key: str) -> Any: ...

    async def set(self, key: str, value: str) -> None: ...


def default_stats() -> dict[str, dict[str, int | None]]:
    """Create the default statistics document."""
    return {
        "played": {difficulty: 0 for difficulty in DIFFICULTIES},
        "won": {difficulty: 0 for difficulty in DIFFICULTIES},
        "best_time": {difficulty: None for difficulty in DIFFICULTIES},
    }


def normalize_stats(candidate: Any) -> dict[str, dict[str, int | None]]:
    """Return a complete, type-safe statistics document from stored data."""
    normalized = default_stats()
    if not isinstance(candidate, dict):
        return normalized

    for section in ("played", "won"):
        stored_section = candidate.get(section)
        if not isinstance(stored_section, dict):
            continue
        for difficulty in DIFFICULTIES:
            value = stored_section.get(difficulty)
            if isinstance(value, int) and value >= 0:
                normalized[section][difficulty] = value

    stored_best_times = candidate.get("best_time")
    if isinstance(stored_best_times, dict):
        for difficulty in DIFFICULTIES:
            value = stored_best_times.get(difficulty)
            if value is None or (isinstance(value, int) and value >= 0):
                normalized["best_time"][difficulty] = value
    return normalized


class StatisticsStore:
    """Store statistics in Flet's native persistent client storage."""

    def __init__(self, preferences: Preferences | None = None) -> None:
        # Keep this reference alive for the lifetime of the game session.
        self._preferences: Preferences = preferences or ft.SharedPreferences()

    async def load(self) -> dict[str, dict[str, int | None]]:
        """Load statistics without making a corrupted preference fatal."""
        try:
            encoded_stats = await self._preferences.get(STATISTICS_KEY)
            decoded_stats = json.loads(encoded_stats) if isinstance(encoded_stats, str) else None
        except Exception:
            # Storage is a convenience feature; a device-level error must not stop play.
            return default_stats()
        return normalize_stats(decoded_stats)

    async def save(self, stats: dict[str, dict[str, int | None]]) -> None:
        """Persist statistics without interrupting a game on a storage error."""
        try:
            await self._preferences.set(STATISTICS_KEY, json.dumps(normalize_stats(stats)))
        except Exception:
            # Storage is a convenience feature; a device-level error must not stop play.
            pass
