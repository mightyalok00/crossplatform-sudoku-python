# Sudoku Flow

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/UI-Flet%20%2F%20Flutter-0284C7.svg?logo=flutter&logoColor=white)](https://flet.dev/)
[![Platform](https://img.shields.io/badge/Platform-Desktop%20%7C%20Web%20%7C%20Mobile-10B981.svg)](https://flet.dev/)

Sudoku Flow is a responsive Sudoku game for desktop, web, and mobile. It includes a unique-solution puzzle generator, pencil notes, undo/redo, hints, mistake tracking, a timer, and local statistics.

## Project layout

```text
.
├── src/sudoku_flow/
│   ├── app.py              # Flet application and user interactions
│   ├── storage.py          # Local statistics persistence
│   ├── core/
│   │   ├── engine.py       # Puzzle generator, solver, and validation
│   │   └── game.py         # In-memory game state and moves
│   └── ui/theme.py         # Shared interface colour tokens
├── tests/                  # Unit tests for game logic and storage
├── main.py                 # Checkout-friendly launcher
├── pyproject.toml          # Package metadata and dependencies
└── requirements.txt        # Compatibility installer entry point
```

## Getting started

Create and activate a virtual environment, then install the app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Run the desktop app:

```powershell
python main.py
```

Run it in a browser (useful for mobile devices on the same network):

```powershell
python main.py --web
```

After installation, these alternatives also work:

```powershell
sudoku-flow
python -m sudoku_flow
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Notes

- Puzzle difficulty targets 40, 32, 26, and 22 clues for Easy through Expert. A puzzle may retain extra clues when needed to preserve a unique solution.
- Statistics are stored in `sudoku_stats.json` in the folder from which the app is launched. Set `SUDOKU_FLOW_STATS_PATH` to store them elsewhere.
- This repository does not currently include a license file; add one before distributing the project under a specific license.
