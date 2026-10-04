"""Persistence for the active Sudoku game."""

import json
import logging

from game import is_valid_state

log = logging.getLogger("app.storage")
_STATE_KEY = "sudoku.active_game"


async def load_game(preferences):
    raw = await preferences.get(_STATE_KEY)
    if not isinstance(raw, str):
        return None
    try:
        state = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        log.warning("Saved game could not be decoded; starting a fresh game")
        return None
    if not is_valid_state(state):
        log.warning("Saved game was invalid; starting a fresh game")
        return None
    return state


async def save_game(preferences, state):
    return await preferences.set(_STATE_KEY, json.dumps(state, separators=(",", ":")))
