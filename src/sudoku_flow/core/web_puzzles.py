"""Instant, uniquely-solvable puzzle templates for static web builds.

Static Flet websites run on a single Pyodide browser thread. Generating a
unique puzzle with backtracking there can freeze the interface, so web builds
use these templates and apply Sudoku-preserving random transformations.
"""

from __future__ import annotations

import random

from .engine import Grid

_PUZZLE_TEMPLATES: dict[str, tuple[Grid, Grid]] = {
    "Easy": (
        [
            [8, 1, 9, 3, 0, 0, 5, 7, 0], [6, 3, 0, 8, 9, 0, 4, 0, 0], [0, 2, 4, 0, 1, 0, 0, 0, 9],
            [0, 0, 0, 0, 4, 0, 3, 0, 7], [0, 0, 3, 0, 0, 9, 2, 0, 4], [9, 0, 2, 7, 3, 0, 0, 0, 0],
            [0, 5, 0, 0, 0, 0, 9, 0, 0], [0, 9, 6, 0, 5, 3, 7, 4, 8], [0, 0, 7, 9, 0, 2, 1, 5, 0],
        ],
        [
            [8, 1, 9, 3, 2, 4, 5, 7, 6], [6, 3, 5, 8, 9, 7, 4, 2, 1], [7, 2, 4, 5, 1, 6, 8, 3, 9],
            [1, 6, 8, 2, 4, 5, 3, 9, 7], [5, 7, 3, 6, 8, 9, 2, 1, 4], [9, 4, 2, 7, 3, 1, 6, 8, 5],
            [3, 5, 1, 4, 7, 8, 9, 6, 2], [2, 9, 6, 1, 5, 3, 7, 4, 8], [4, 8, 7, 9, 6, 2, 1, 5, 3],
        ],
    ),
    "Medium": (
        [
            [0, 1, 4, 5, 2, 8, 0, 7, 9], [0, 5, 0, 7, 0, 0, 0, 0, 0], [0, 9, 0, 0, 6, 0, 0, 8, 0],
            [5, 3, 0, 6, 0, 0, 0, 0, 8], [0, 0, 1, 0, 3, 0, 0, 4, 7], [0, 0, 8, 0, 0, 0, 0, 0, 0],
            [1, 0, 3, 9, 0, 7, 0, 0, 0], [0, 2, 6, 0, 0, 5, 0, 0, 0], [0, 4, 5, 0, 0, 0, 0, 3, 1],
        ],
        [
            [6, 1, 4, 5, 2, 8, 3, 7, 9], [8, 5, 2, 7, 9, 3, 4, 1, 6], [3, 9, 7, 4, 6, 1, 2, 8, 5],
            [5, 3, 9, 6, 7, 4, 1, 2, 8], [2, 6, 1, 8, 3, 9, 5, 4, 7], [4, 7, 8, 1, 5, 2, 9, 6, 3],
            [1, 8, 3, 9, 4, 7, 6, 5, 2], [7, 2, 6, 3, 1, 5, 8, 9, 4], [9, 4, 5, 2, 8, 6, 7, 3, 1],
        ],
    ),
    "Hard": (
        [
            [4, 0, 0, 0, 7, 0, 6, 9, 0], [3, 8, 0, 0, 0, 0, 2, 0, 4], [0, 0, 0, 0, 0, 3, 0, 5, 0],
            [0, 0, 1, 0, 8, 0, 0, 0, 0], [0, 7, 0, 0, 9, 0, 0, 1, 6], [0, 0, 4, 0, 0, 0, 0, 0, 7],
            [0, 0, 8, 3, 5, 0, 1, 0, 0], [0, 2, 6, 0, 0, 0, 0, 0, 0], [0, 0, 0, 2, 0, 6, 0, 0, 0],
        ],
        [
            [4, 1, 2, 8, 7, 5, 6, 9, 3], [3, 8, 5, 1, 6, 9, 2, 7, 4], [7, 6, 9, 4, 2, 3, 8, 5, 1],
            [6, 5, 1, 7, 8, 4, 3, 2, 9], [8, 7, 3, 5, 9, 2, 4, 1, 6], [2, 9, 4, 6, 3, 1, 5, 8, 7],
            [9, 4, 8, 3, 5, 7, 1, 6, 2], [1, 2, 6, 9, 4, 8, 7, 3, 5], [5, 3, 7, 2, 1, 6, 9, 4, 8],
        ],
    ),
    "Expert": (
        [
            [0, 6, 0, 0, 9, 0, 0, 7, 0], [5, 0, 9, 0, 0, 1, 0, 4, 0], [0, 4, 0, 0, 0, 0, 0, 0, 6],
            [0, 0, 0, 2, 8, 0, 1, 0, 0], [0, 3, 0, 1, 0, 5, 0, 0, 0], [7, 0, 2, 3, 0, 0, 0, 0, 9],
            [0, 0, 0, 0, 0, 4, 0, 0, 0], [0, 0, 0, 0, 0, 0, 2, 0, 0], [0, 0, 0, 7, 3, 0, 0, 0, 0],
        ],
        [
            [8, 6, 1, 4, 9, 3, 5, 7, 2], [5, 7, 9, 6, 2, 1, 3, 4, 8], [2, 4, 3, 8, 5, 7, 9, 1, 6],
            [6, 5, 4, 2, 8, 9, 1, 3, 7], [9, 3, 8, 1, 7, 5, 6, 2, 4], [7, 1, 2, 3, 4, 6, 8, 5, 9],
            [3, 2, 5, 9, 6, 4, 7, 8, 1], [4, 9, 7, 5, 1, 8, 2, 6, 3], [1, 8, 6, 7, 3, 2, 4, 9, 5],
        ],
    ),
}


def _shuffled_unit_indices() -> list[int]:
    """Return a Sudoku-safe ordering of rows or columns."""
    unit_groups = list(range(3))
    random.shuffle(unit_groups)
    indices: list[int] = []
    for group in unit_groups:
        members = list(range(group * 3, group * 3 + 3))
        random.shuffle(members)
        indices.extend(members)
    return indices


def _transform(board: Grid, row_order: list[int], column_order: list[int], digit_map: dict[int, int]) -> Grid:
    return [
        [digit_map[board[row][column]] for column in column_order]
        for row in row_order
    ]


def get_web_puzzle(difficulty: str) -> tuple[Grid, Grid]:
    """Return a fast, randomized variation of a unique puzzle template."""
    puzzle, solution = _PUZZLE_TEMPLATES.get(difficulty, _PUZZLE_TEMPLATES["Medium"])
    row_order = _shuffled_unit_indices()
    column_order = _shuffled_unit_indices()
    digits = list(range(1, 10))
    random.shuffle(digits)
    digit_map = {0: 0, **dict(zip(range(1, 10), digits))}

    return (
        _transform(puzzle, row_order, column_order, digit_map),
        _transform(solution, row_order, column_order, digit_map),
    )
