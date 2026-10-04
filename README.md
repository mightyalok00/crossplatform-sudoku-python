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
│   │   ├── game.py         # In-memory game state and moves
│   │   └── web_puzzles.py  # Instant, randomized web puzzle templates
│   └── ui/theme.py         # Shared interface colour tokens
├── tests/                  # Unit tests for game logic and storage
├── .github/workflows/      # Test and GitHub Pages deployment automation
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

## Deploy

Every push to `main` builds the static web app and deploys it to GitHub Pages. Before the first deployment, open the repository's **Settings → Pages** and select **GitHub Actions** as the source.

The workflow sets the correct project subdirectory and hash routing for GitHub Pages. It uses persistent Flet client storage for statistics and instant randomized puzzle templates in browser builds, so the interface is not held up by backtracking generation.

To build a Windows bundle locally, install Flutter plus Visual Studio's **Desktop development with C++** workload, then run:

```powershell
flet build windows
```

## Notes

- Puzzle difficulty targets 40, 32, 26, and 22 clues for Easy through Expert. A puzzle may retain extra clues when needed to preserve a unique solution.
- Statistics persist through Flet's native client storage: browser local storage on the web, a local JSON file on desktop, and the platform preference store on mobile.
- This repository does not currently include a license file; add one before distributing the project under a specific license.
