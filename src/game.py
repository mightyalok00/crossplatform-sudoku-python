"""Sudoku rules and puzzle generation; this module has no Flet dependency."""

from __future__ import annotations

import random

SIZE = 9
DIFFICULTY_BLANKS = {"easy": 38, "medium": 48, "hard": 54}


def new_game(difficulty: str = "medium") -> dict:
    """Create a complete valid Sudoku solution and a puzzle with blanks."""
    difficulty = difficulty.lower()
    if difficulty not in DIFFICULTY_BLANKS:
        difficulty = "medium"

    digit_map = list(range(1, 10))
    random.shuffle(digit_map)
    bands = list(range(3))
    stacks = list(range(3))
    random.shuffle(bands)
    random.shuffle(stacks)
    rows = [band * 3 + row for band in bands for row in random.sample(range(3), 3)]
    cols = [stack * 3 + col for stack in stacks for col in random.sample(range(3), 3)]

    solution = [
        [digit_map[(row * 3 + row // 3 + col) % 9] for col in cols]
        for row in rows
    ]
    puzzle = [row[:] for row in solution]
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)
    for row, col in positions[: DIFFICULTY_BLANKS[difficulty]]:
        puzzle[row][col] = 0

    return {
        "puzzle": puzzle,
        "board": [row[:] for row in puzzle],
        "solution": solution,
        "difficulty": difficulty,
        "elapsed": 0,
        "selected": [0, 0],
        "hints": 0,
    }


def is_valid_state(state: object) -> bool:
    if not isinstance(state, dict):
        return False
    try:
        for key in ("puzzle", "board", "solution"):
            grid = state[key]
            if len(grid) != SIZE or any(len(row) != SIZE for row in grid):
                return False
            if any(not isinstance(value, int) or value < 0 or value > 9 for row in grid for value in row):
                return False
        if state["difficulty"] not in DIFFICULTY_BLANKS:
            return False
        if not isinstance(state["elapsed"], int) or state["elapsed"] < 0:
            return False
        selected = state.get("selected", [0, 0])
        if len(selected) != 2 or any(not isinstance(i, int) or not 0 <= i < SIZE for i in selected):
            return False
        return True
    except (KeyError, TypeError):
        return False


def conflicts(board: list[list[int]]) -> set[tuple[int, int]]:
    """Return cells participating in a repeated non-zero row, column, or box value."""
    bad: set[tuple[int, int]] = set()
    groups: list[list[tuple[int, int]]] = []
    groups.extend([[(r, c) for c in range(SIZE)] for r in range(SIZE)])
    groups.extend([[(r, c) for r in range(SIZE)] for c in range(SIZE)])
    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            groups.append([
                (r, c)
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
            ])

    for group in groups:
        seen: dict[int, list[tuple[int, int]]] = {}
        for row, col in group:
            value = board[row][col]
            if value:
                seen.setdefault(value, []).append((row, col))
        for cells in seen.values():
            if len(cells) > 1:
                bad.update(cells)
    return bad


def solved(state: dict) -> bool:
    return state["board"] == state["solution"]


def next_hint(state: dict) -> tuple[int, int] | None:
    row, col = state.get("selected", [0, 0])
    if state["board"][row][col] == 0:
        return row, col
    for r in range(SIZE):
        for c in range(SIZE):
            if state["board"][r][c] == 0:
                return r, c
    return None
