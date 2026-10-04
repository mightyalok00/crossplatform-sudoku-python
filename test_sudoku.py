"""
Comprehensive test suite for Sudoku engine, solver, and game state.
"""

from sudoku_generator import SudokuEngine
from game_state import SudokuGame

def test_engine_generation_and_uniqueness():
    print("Testing Sudoku Generation...")
    for diff in ["Easy", "Medium", "Hard", "Expert"]:
        puzzle, solution = SudokuEngine.generate_puzzle(diff)
        clues = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] != 0)
        print(f"  {diff}: {clues} clues generated")
        assert clues > 0, f"Puzzle for {diff} must have clues"
        
        # Verify solution correctness
        is_solvable, count, solved = SudokuEngine.solve_grid(puzzle, count_solutions=True, max_count=2)
        assert is_solvable, f"{diff} puzzle must be solvable"
        assert count == 1, f"{diff} puzzle must have exactly 1 unique solution (got {count})"
        assert solved == solution, f"{diff} solver output must match generated full solution"
    print("Generation & Uniqueness tests PASSED! [OK]")

def test_game_state_logic():
    print("\nTesting Game State Logic...")
    game = SudokuGame(difficulty="Easy")
    
    # 1. Selection
    game.select_cell(4, 4)
    assert game.selected_cell == (4, 4)
    
    # 2. Undo / Redo with number entry
    empty_cell = None
    for r in range(9):
        for c in range(9):
            if not game.is_given(r, c):
                empty_cell = (r, c)
                break
        if empty_cell:
            break
            
    r, c = empty_cell
    game.select_cell(r, c)
    correct_val = game.solution_grid[r][c]
    
    # Enter correct number
    res = game.enter_number(correct_val)
    assert res["status"] == "value_entered"
    assert not res["is_mistake"]
    assert game.current_grid[r][c] == correct_val
    
    # Undo
    assert game.undo()
    assert game.current_grid[r][c] == 0
    
    # Redo
    assert game.redo()
    assert game.current_grid[r][c] == correct_val
    
    # 3. Notes / Pencil marks
    game.erase_selected()
    assert game.current_grid[r][c] == 0
    
    game.toggle_notes_mode()
    assert game.notes_mode
    game.enter_number(1)
    game.enter_number(5)
    assert 1 in game.notes_grid[r][c]
    assert 5 in game.notes_grid[r][c]
    
    # Toggle note off
    game.enter_number(1)
    assert 1 not in game.notes_grid[r][c]
    assert 5 in game.notes_grid[r][c]
    
    # Undo note
    game.undo()
    assert 1 in game.notes_grid[r][c]
    
    # 4. Mistake tracking
    game.toggle_notes_mode()
    assert not game.notes_mode
    wrong_val = (correct_val % 9) + 1
    m_res = game.enter_number(wrong_val)
    assert m_res["is_mistake"]
    assert game.mistakes_count == 1
    
    # 5. Hints
    hint_res = game.use_hint()
    assert hint_res is not None
    assert game.hints_used == 1
    
    print("Game State Logic tests PASSED! [OK]")

if __name__ == "__main__":
    test_engine_generation_and_uniqueness()
    test_game_state_logic()
    print("\nALL SUDOKU TESTS PASSED! [SUCCESS]")
