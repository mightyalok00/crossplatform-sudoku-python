"""Persistence helpers for local game statistics."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DIFFICULTIES = ("Easy", "Medium", "Hard", "Expert")
STATS_FILENAME = "sudoku_stats.json"
STATS_PATH_ENVIRONMENT_VARIABLE = "SUDOKU_FLOW_STATS_PATH"


def stats_path() -> Path:
    """Return the configured statistics path, defaulting to the launch folder."""
    configured_path = os.getenv(STATS_PATH_ENVIRONMENT_VARIABLE)
    return Path(configured_path) if configured_path else Path.cwd() / STATS_FILENAME


def default_stats() -> dict[str, dict[str, int | None]]:
    """Create the default statistics document."""
    return {
        "played": {difficulty: 0 for difficulty in DIFFICULTIES},
        "won": {difficulty: 0 for difficulty in DIFFICULTIES},
        "best_time": {difficulty: None for difficulty in DIFFICULTIES},
    }


def load_stats() -> dict[str, dict[str, Any]]:
    """Load local statistics, falling back safely for missing or invalid data."""
    defaults = default_stats()
    try:
        with stats_path().open("r", encoding="utf-8") as stats_file:
            saved_stats = json.load(stats_file)
    except (OSError, json.JSONDecodeError):
        return defaults

    if not isinstance(saved_stats, dict):
        return defaults

    for section, values in defaults.items():
        saved_values = saved_stats.get(section)
        if not isinstance(saved_values, dict):
            continue
        for difficulty in values:
            if difficulty in saved_values:
                values[difficulty] = saved_values[difficulty]
    return defaults


def save_stats(stats: dict[str, dict[str, Any]]) -> None:
    """Persist local statistics without interrupting a game on a disk error."""
    try:
        destination = stats_path()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as stats_file:
            json.dump(stats, stats_file, indent=2)
    except OSError:
        pass
