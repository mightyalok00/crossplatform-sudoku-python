# Modern Sudoku Pro (Desktop & Mobile)

A sleek, responsive, full-featured Sudoku game built with Python and **Flet** (Flutter engine for Python). Playable seamlessly on **Desktop (Windows/Mac/Linux)** and **Mobile / Web Browsers**.

---

## 🌟 Key Features

- 🧩 **Smart Puzzle Generator & Solver**:
  - 4 Difficulty tiers: **Easy**, **Medium**, **Hard**, and **Expert**.
  - Guaranteed unique solution using backtracking solver with Minimum Remaining Values (MRV) heuristic.
- ⚡ **Mistake Feedback & Conflict Highlighting**:
  - Live duplicate and error detection with soft crimson highlights.
  - Optional strict 3-mistake limit toggle.
- ✏️ **Pencil Notes Mode**:
  - Real-time mini 3x3 notes/pencil marks in empty cells.
  - Auto-clearing peer notes when a correct number is placed.
- 🎮 **Cross-Platform Responsive Controls**:
  - **On-Screen Keypad** with placed number counts & remaining trackers.
  - **Full Keyboard Navigation**: Arrow keys / WASD, 1-9 numbers, Backspace/Delete to erase, `N` for Notes, `U` for Undo, `Y` for Redo, `H` for Hint, and Space/`P` to Pause.
- ⏱️ **Timer & Game Stats**:
  - Live timer with pause/resume functionality.
  - Persistent game statistics (games played, win rates, and best times).
- 💡 **Smart Hints & Action History**:
  - Undo and Redo move history stack.
  - Intelligent Hint assistant to get unstuck.
- 🎨 **Premium Modern Dark Glassmorphic Aesthetic**:
  - Soft luminous cell glow, row/column/box peer guides, and victory celebration dialog.

---

## 🚀 How to Run

### 1. Run as Native Desktop App
```bash
python main.py
```

### 2. Run as Web / Mobile App (Access from Phone or Browser)
```bash
flet run --web main.py
```
*Tip: Open the printed local network IP address on your phone to play natively on mobile!*

---

## 📁 Project Structure

- [`main.py`](file:///C:/Users/Alok%20Agarwal/.gemini/antigravity-ide/scratch/sudoku-flet/main.py): Main UI application and event controllers in Flet.
- [`game_state.py`](file:///C:/Users/Alok%20Agarwal/.gemini/antigravity-ide/scratch/sudoku-flet/game_state.py): Game logic, move history, pencil notes, mistake limits, and hint generator.
- [`sudoku_generator.py`](file:///C:/Users/Alok%20Agarwal/.gemini/antigravity-ide/scratch/sudoku-flet/sudoku_generator.py): Backtracking puzzle generator, solver, and conflict checker.
- [`test_sudoku.py`](file:///C:/Users/Alok%20Agarwal/.gemini/antigravity-ide/scratch/sudoku-flet/test_sudoku.py): Unit test suite.
