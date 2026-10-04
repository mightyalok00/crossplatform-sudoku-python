"""
Sudoku Generator and Solver Engine.
Generates valid Sudoku puzzles with guaranteed unique solutions across multiple difficulty levels.
"""

import random
from copy import deepcopy
from typing import List, Set, Tuple

Grid = List[List[int]]

class SudokuEngine:
    DIFFICULTIES = {
        "Easy": {"clues": 40, "name": "Easy"},
        "Medium": {"clues": 32, "name": "Medium"},
        "Hard": {"clues": 26, "name": "Hard"},
        "Expert": {"clues": 22, "name": "Expert"}
    }

    @staticmethod
    def create_empty_grid() -> Grid:
        return [[0 for _ in range(9)] for _ in range(9)]

    @staticmethod
    def is_valid_move(grid: Grid, row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid in the given grid."""
        # Row check
        for c in range(9):
            if c != col and grid[row][c] == num:
                return False
        
        # Col check
        for r in range(9):
            if r != row and grid[r][col] == num:
                return False
        
        # 3x3 Block check
        box_r, box_c = (row // 3) * 3, (col // 3) * 3
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if (r != row or c != col) and grid[r][c] == num:
                    return False
        
        return True

    @classmethod
    def solve_grid(cls, grid: Grid, count_solutions: bool = False, max_count: int = 2) -> Tuple[bool, int, Grid]:
        """
        Backtracking solver.
        If count_solutions is True, counts up to max_count solutions.
        Returns (is_solvable, solution_count, solved_grid).
        """
        solved_grid = deepcopy(grid)
        solutions = []

        def solve():
            if len(solutions) >= max_count:
                return
            
            # Find empty cell with Minimum Remaining Values (MRV heuristic)
            min_options = 10
            best_cell = None
            best_choices = []

            for r in range(9):
                for c in range(9):
                    if solved_grid[r][c] == 0:
                        choices = [n for n in range(1, 10) if cls.is_valid_move(solved_grid, r, c, n)]
                        if len(choices) < min_options:
                            min_options = len(choices)
                            best_cell = (r, c)
                            best_choices = choices
                            if min_options == 0:
                                return  # Dead end

            if best_cell is None:
                solutions.append(deepcopy(solved_grid))
                return

            r, c = best_cell
            for num in best_choices:
                solved_grid[r][c] = num
                solve()
                solved_grid[r][c] = 0
                if len(solutions) >= max_count and not count_solutions:
                    break

        solve()
        sol_count = len(solutions)
        final_grid = solutions[0] if sol_count > 0 else deepcopy(grid)
        return (sol_count > 0, sol_count, final_grid)

    @classmethod
    def generate_full_grid(cls) -> Grid:
        """Generates a complete, randomized valid 9x9 Sudoku board."""
        grid = cls.create_empty_grid()

        def fill_board():
            for r in range(9):
                for c in range(9):
                    if grid[r][c] == 0:
                        nums = list(range(1, 10))
                        random.shuffle(nums)
                        for num in nums:
                            if cls.is_valid_move(grid, r, c, num):
                                grid[r][c] = num
                                if fill_board():
                                    return True
                                grid[r][c] = 0
                        return False
            return True

        fill_board()
        return grid

    @classmethod
    def generate_puzzle(cls, difficulty: str = "Medium") -> Tuple[Grid, Grid]:
        """
        Generates a puzzle with a single unique solution.
        Returns (puzzle_grid, solution_grid).
        """
        diff_info = cls.DIFFICULTIES.get(difficulty, cls.DIFFICULTIES["Medium"])
        target_clues = diff_info["clues"]
        
        full_grid = cls.generate_full_grid()
        puzzle_grid = deepcopy(full_grid)
        
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        
        current_clues = 81
        for r, c in cells:
            if current_clues <= target_clues:
                break
            
            val = puzzle_grid[r][c]
            puzzle_grid[r][c] = 0
            
            # Verify uniqueness
            _, count, _ = cls.solve_grid(puzzle_grid, count_solutions=True, max_count=2)
            if count != 1:
                # Restoring if removing breaks uniqueness
                puzzle_grid[r][c] = val
            else:
                current_clues -= 1
                
        return puzzle_grid, full_grid

    @classmethod
    def get_conflicts(cls, grid: Grid) -> Set[Tuple[int, int]]:
        """Returns set of all (row, col) cells that violate Sudoku rules with another cell."""
        conflicts = set()
        
        # Rows
        for r in range(9):
            seen = {}
            for c in range(9):
                val = grid[r][c]
                if val != 0:
                    if val in seen:
                        conflicts.add((r, c))
                        conflicts.add((r, seen[val]))
                    else:
                        seen[val] = c
                        
        # Columns
        for c in range(9):
            seen = {}
            for r in range(9):
                val = grid[r][c]
                if val != 0:
                    if val in seen:
                        conflicts.add((r, c))
                        conflicts.add((seen[val], c))
                    else:
                        seen[val] = r
                        
        # 3x3 Blocks
        for br in range(3):
            for bc in range(3):
                seen = {}
                for r in range(br * 3, br * 3 + 3):
                    for c in range(bc * 3, bc * 3 + 3):
                        val = grid[r][c]
                        if val != 0:
                            if val in seen:
                                conflicts.add((r, c))
                                conflicts.add(seen[val])
                            else:
                                seen[val] = (r, c)
                                
        return conflicts
