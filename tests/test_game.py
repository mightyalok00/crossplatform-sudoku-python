"""Unit tests for the Sudoku engine, game state, web puzzles, and storage."""

import asyncio
import unittest
from typing import Any
from unittest.mock import patch

from sudoku_flow.core.engine import SudokuEngine
from sudoku_flow.core.game import SudokuGame
from sudoku_flow.core.web_puzzles import get_web_puzzle
from sudoku_flow.storage import StatisticsStore, default_stats, normalize_stats


class SudokuEngineTests(unittest.TestCase):
    def test_generated_puzzles_have_one_solution(self) -> None:
        for difficulty in SudokuEngine.DIFFICULTIES:
            with self.subTest(difficulty=difficulty):
                puzzle, solution = SudokuEngine.generate_puzzle(difficulty)
                is_solvable, solution_count, solved = SudokuEngine.solve_grid(
                    puzzle, count_solutions=True, max_count=2
                )

                self.assertGreater(sum(value != 0 for row in puzzle for value in row), 0)
                self.assertTrue(is_solvable)
                self.assertEqual(solution_count, 1)
                self.assertEqual(solved, solution)

    def test_conflicts_identifies_row_column_and_box_duplicates(self) -> None:
        grid = SudokuEngine.create_empty_grid()
        grid[0][0] = grid[0][1] = 1
        grid[1][0] = 1

        self.assertEqual(SudokuEngine.get_conflicts(grid), {(0, 0), (0, 1), (1, 0)})


class WebPuzzleTests(unittest.TestCase):
    def test_web_puzzles_are_unique_randomized_variations(self) -> None:
        for difficulty in SudokuEngine.DIFFICULTIES:
            with self.subTest(difficulty=difficulty):
                puzzle, solution = get_web_puzzle(difficulty)
                is_solvable, solution_count, solved = SudokuEngine.solve_grid(
                    puzzle, count_solutions=True, max_count=2
                )

                self.assertTrue(is_solvable)
                self.assertEqual(solution_count, 1)
                self.assertEqual(solved, solution)

    @patch("sudoku_flow.core.game.sys.platform", "emscripten")
    def test_game_uses_instant_templates_in_static_web_builds(self) -> None:
        game = SudokuGame(difficulty="Medium")

        self.assertEqual(sum(value != 0 for row in game.initial_grid for value in row), 32)
        self.assertTrue(SudokuEngine.solve_grid(game.initial_grid, count_solutions=True)[0])


class SudokuGameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.game = SudokuGame(difficulty="Easy")
        self.row, self.column = next(
            (row, column)
            for row in range(9)
            for column in range(9)
            if not self.game.is_given(row, column)
        )
        self.game.select_cell(self.row, self.column)

    def test_correct_entry_can_be_undone_and_redone(self) -> None:
        answer = self.game.solution_grid[self.row][self.column]

        result = self.game.enter_number(answer)

        self.assertEqual(result["status"], "value_entered")
        self.assertFalse(result["is_mistake"])
        self.assertEqual(self.game.current_grid[self.row][self.column], answer)
        self.assertTrue(self.game.undo())
        self.assertEqual(self.game.current_grid[self.row][self.column], 0)
        self.assertTrue(self.game.redo())
        self.assertEqual(self.game.current_grid[self.row][self.column], answer)

    def test_notes_can_be_toggled_and_undone(self) -> None:
        self.game.toggle_notes_mode()
        self.game.enter_number(1)
        self.game.enter_number(5)
        self.game.enter_number(1)

        self.assertEqual(self.game.notes_grid[self.row][self.column], {5})
        self.assertTrue(self.game.undo())
        self.assertEqual(self.game.notes_grid[self.row][self.column], {1, 5})

    def test_hint_fills_the_selected_empty_cell(self) -> None:
        hint = self.game.use_hint()

        self.assertEqual(
            hint,
            (self.row, self.column, self.game.solution_grid[self.row][self.column]),
        )
        self.assertEqual(self.game.hints_used, 1)


class MemoryPreferences:
    """Minimal async fake for testing Flet's shared-preferences integration."""

    def __init__(self) -> None:
        self.values: dict[str, Any] = {}

    async def get(self, key: str) -> Any:
        return self.values.get(key)

    async def set(self, key: str, value: str) -> None:
        self.values[key] = value


class StorageTests(unittest.TestCase):
    def test_statistics_round_trip_through_client_storage(self) -> None:
        preferences = MemoryPreferences()
        store = StatisticsStore(preferences)
        stats = default_stats()
        stats["played"]["Easy"] = 2
        stats["best_time"]["Easy"] = 73

        async def save_and_load() -> dict[str, dict[str, int | None]]:
            await store.save(stats)
            return await store.load()

        self.assertEqual(asyncio.run(save_and_load()), stats)

    def test_invalid_statistics_are_replaced_with_safe_defaults(self) -> None:
        self.assertEqual(normalize_stats({"played": {"Easy": -1}}), default_stats())


if __name__ == "__main__":
    unittest.main()
