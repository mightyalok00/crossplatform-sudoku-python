"""
Game state and controller for Sudoku.
Handles moves, undo/redo, pencil notes, mistakes, hints, and game completion.
"""

import sys
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from .engine import Grid, SudokuEngine
from .web_puzzles import get_web_puzzle

@dataclass
class Move:
    row: int
    col: int
    old_value: int
    new_value: int
    old_notes: Set[int]
    new_notes: Set[int]
    was_mistake: bool = False

class SudokuGame:
    def __init__(self, difficulty: str = "Medium"):
        self.difficulty = difficulty
        self.max_mistakes = 3
        self.strict_mistakes = True
        self.auto_clear_notes = True
        self.notes_mode = False
        
        self.initial_grid: Grid = []
        self.solution_grid: Grid = []
        self.current_grid: Grid = []
        self.notes_grid: List[List[Set[int]]] = []
        
        self.selected_cell: Optional[Tuple[int, int]] = (0, 0)
        self.mistakes_count = 0
        self.hints_used = 0
        self.undo_stack: List[Move] = []
        self.redo_stack: List[Move] = []
        
        self.is_game_over = False
        self.is_won = False
        self.is_paused = False
        self.elapsed_seconds = 0
        
        self.start_new_game(difficulty)

    def start_new_game(self, difficulty: Optional[str] = None):
        """Starts a fresh new puzzle."""
        if difficulty:
            self.difficulty = difficulty
            
        if sys.platform == "emscripten":
            self.initial_grid, self.solution_grid = get_web_puzzle(self.difficulty)
        else:
            self.initial_grid, self.solution_grid = SudokuEngine.generate_puzzle(self.difficulty)
        self.current_grid = deepcopy(self.initial_grid)
        self.notes_grid = [[set() for _ in range(9)] for _ in range(9)]
        
        self.mistakes_count = 0
        self.hints_used = 0
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.is_game_over = False
        self.is_won = False
        self.is_paused = False
        self.elapsed_seconds = 0
        self.selected_cell = (0, 0)

    def restart_current_game(self):
        """Resets the current puzzle back to its initial state."""
        self.current_grid = deepcopy(self.initial_grid)
        self.notes_grid = [[set() for _ in range(9)] for _ in range(9)]
        self.mistakes_count = 0
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.is_game_over = False
        self.is_won = False
        self.is_paused = False
        self.elapsed_seconds = 0

    def is_given(self, row: int, col: int) -> bool:
        """Returns True if the cell was given in the initial puzzle."""
        return self.initial_grid[row][col] != 0

    def select_cell(self, row: int, col: int):
        """Sets the currently active cell."""
        if 0 <= row < 9 and 0 <= col < 9:
            self.selected_cell = (row, col)

    def toggle_notes_mode(self):
        """Toggles between normal input mode and pencil/notes mode."""
        self.notes_mode = not self.notes_mode

    def enter_number(self, num: int) -> Dict[str, Any]:
        """
        Inputs a number (1-9) into the selected cell.
        Returns a dict describing the result of the action.
        """
        if self.is_game_over or self.is_won or self.is_paused:
            return {"status": "inactive"}
            
        if self.selected_cell is None:
            return {"status": "no_selection"}
            
        r, c = self.selected_cell
        if self.is_given(r, c):
            return {"status": "given_cell"}
            
        if self.notes_mode:
            # Pencil / Notes mode
            old_notes = set(self.notes_grid[r][c])
            new_notes = set(old_notes)
            
            if num in new_notes:
                new_notes.remove(num)
            else:
                new_notes.add(num)
                
            move = Move(
                row=r, col=c,
                old_value=self.current_grid[r][c],
                new_value=self.current_grid[r][c],
                old_notes=old_notes,
                new_notes=new_notes
            )
            self.undo_stack.append(move)
            self.redo_stack.clear()
            self.notes_grid[r][c] = new_notes
            return {"status": "note_toggled", "num": num, "cell": (r, c)}

        else:
            # Value input mode
            old_val = self.current_grid[r][c]
            old_notes = set(self.notes_grid[r][c])
            correct_val = self.solution_grid[r][c]
            
            if old_val == num:
                # Same number re-entered: no-op or clear
                return {"status": "same_value"}
                
            is_mistake = (num != correct_val)
            
            if is_mistake:
                self.mistakes_count += 1
                if self.strict_mistakes and self.mistakes_count >= self.max_mistakes:
                    self.is_game_over = True
                    
            move = Move(
                row=r, col=c,
                old_value=old_val,
                new_value=num,
                old_notes=old_notes,
                new_notes=set(), # Cleared on number entry
                was_mistake=is_mistake
            )
            self.undo_stack.append(move)
            self.redo_stack.clear()
            
            self.current_grid[r][c] = num
            self.notes_grid[r][c].clear()
            
            # Auto-remove notes in same row, col, box if correct
            if not is_mistake and self.auto_clear_notes:
                self._clear_peer_notes(r, c, num)
                
            # Check victory
            self.check_win()
            
            return {
                "status": "value_entered",
                "num": num,
                "is_mistake": is_mistake,
                "mistakes": self.mistakes_count,
                "game_over": self.is_game_over,
                "is_won": self.is_won
            }

    def _clear_peer_notes(self, row: int, col: int, num: int):
        """Removes `num` from notes in the same row, col, and 3x3 block."""
        for c in range(9):
            self.notes_grid[row][c].discard(num)
        for r in range(9):
            self.notes_grid[r][col].discard(num)
        box_r, box_c = (row // 3) * 3, (col // 3) * 3
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                self.notes_grid[r][c].discard(num)

    def erase_selected(self) -> bool:
        """Erases value or notes in the selected cell."""
        if self.is_game_over or self.is_won or self.selected_cell is None:
            return False
            
        r, c = self.selected_cell
        if self.is_given(r, c):
            return False
            
        old_val = self.current_grid[r][c]
        old_notes = set(self.notes_grid[r][c])
        
        if old_val == 0 and not old_notes:
            return False
            
        move = Move(
            row=r, col=c,
            old_value=old_val,
            new_value=0,
            old_notes=old_notes,
            new_notes=set()
        )
        self.undo_stack.append(move)
        self.redo_stack.clear()
        
        self.current_grid[r][c] = 0
        self.notes_grid[r][c].clear()
        return True

    def undo(self) -> bool:
        """Undoes the last move."""
        if not self.undo_stack or self.is_game_over or self.is_won:
            return False
            
        move = self.undo_stack.pop()
        self.redo_stack.append(move)
        
        self.current_grid[move.row][move.col] = move.old_value
        self.notes_grid[move.row][move.col] = set(move.old_notes)
        self.selected_cell = (move.row, move.col)
        
        # If the undone move was a mistake, restore mistake count
        if move.was_mistake and self.mistakes_count > 0:
            self.mistakes_count -= 1
            
        return True

    def redo(self) -> bool:
        """Redoes the last undone move."""
        if not self.redo_stack or self.is_game_over or self.is_won:
            return False
            
        move = self.redo_stack.pop()
        self.undo_stack.append(move)
        
        self.current_grid[move.row][move.col] = move.new_value
        self.notes_grid[move.row][move.col] = set(move.new_notes)
        self.selected_cell = (move.row, move.col)
        
        if move.was_mistake:
            self.mistakes_count += 1
            if self.strict_mistakes and self.mistakes_count >= self.max_mistakes:
                self.is_game_over = True
                
        self.check_win()
        return True

    def use_hint(self) -> Optional[Tuple[int, int, int]]:
        """
        Gives a hint by filling in the correct value for selected or an empty cell.
        Returns (row, col, value).
        """
        if self.is_game_over or self.is_won:
            return None
            
        target_cell = None
        
        # If user has an empty non-given cell or mistaken cell selected, hint that cell
        if self.selected_cell:
            r, c = self.selected_cell
            if not self.is_given(r, c) and self.current_grid[r][c] != self.solution_grid[r][c]:
                target_cell = (r, c)
                
        # Otherwise find first empty / wrong cell
        if not target_cell:
            empty_cells = [
                (r, c) for r in range(9) for c in range(9)
                if not self.is_given(r, c) and self.current_grid[r][c] != self.solution_grid[r][c]
            ]
            if empty_cells:
                target_cell = empty_cells[0]
                
        if not target_cell:
            return None
            
        r, c = target_cell
        val = self.solution_grid[r][c]
        
        old_val = self.current_grid[r][c]
        old_notes = set(self.notes_grid[r][c])
        
        move = Move(
            row=r, col=c,
            old_value=old_val,
            new_value=val,
            old_notes=old_notes,
            new_notes=set()
        )
        self.undo_stack.append(move)
        self.redo_stack.clear()
        
        self.current_grid[r][c] = val
        self.notes_grid[r][c].clear()
        self.selected_cell = (r, c)
        self.hints_used += 1
        
        if self.auto_clear_notes:
            self._clear_peer_notes(r, c, val)
            
        self.check_win()
        return (r, c, val)

    def check_win(self) -> bool:
        """Checks if the board is completely and correctly filled."""
        for r in range(9):
            for c in range(9):
                if self.current_grid[r][c] != self.solution_grid[r][c]:
                    self.is_won = False
                    return False
        self.is_won = True
        return True

    def get_number_counts(self) -> Dict[int, int]:
        """Returns the count of placed instances for each number (1-9)."""
        counts = {n: 0 for n in range(1, 10)}
        for r in range(9):
            for c in range(9):
                val = self.current_grid[r][c]
                if 1 <= val <= 9:
                    counts[val] += 1
        return counts
