# 🧩 Sudoku Flow - Modern Cross-Platform Sudoku Game

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/UI-Flet%201.0%2B%20(Flutter)-0284C7.svg?logo=flutter&logoColor=white)](https://flet.dev/)
[![Platform](https://img.shields.io/badge/Platform-Desktop%20%7C%20Web%20%7C%20Mobile-10B981.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

> **Sudoku Flow** is a sleek, modern, and responsive Sudoku game built with **Python** and **Flet** (Flutter engine for Python). Playable seamlessly across **Desktop (Windows, macOS, Linux)**, **Mobile (Android/iOS)**, and **Web Browsers**.

---

## 🏷️ Topics & Tags
python • let • lutter • sudoku • game-development • cross-platform • desktop-app • mobile-app • pwa • puzzle-game • acktracking-algorithm

---

## 🌟 Key Features

- 🎲 **Smart Puzzle Generator & Solver**:
  - 4 Difficulty tiers: **Easy** (40 clues), **Medium** (32 clues), **Hard** (26 clues), and **Expert** (22 clues).
  - Guaranteed unique solution validation using a backtracking solver with **Minimum Remaining Values (MRV)** heuristic.
- ⚡ **Mistake Feedback & Visual Conflict Glow**:
  - Instant duplicate and error detection with soft crimson highlights.
  - Optional strict 3-mistake limit mode with configurable settings.
- ✏️ **Pencil Notes Mode**:
  - Live 3x3 candidate pencil marks inside empty cells.
  - Auto-clears peer candidate notes in same row, column, and 3x3 block upon number placement.
- 🎮 **Cross-Platform Responsive Controls**:
  - **On-Screen Keypad** with placed number count badges & remaining trackers.
  - **Full Keyboard Navigation & Shortcuts**:
    - Arrow Keys / WASD: Move cell selection
    - 1 – 9: Place number / Toggle pencil note
    - Backspace / Delete: Erase cell
    - N: Toggle Pencil Notes mode
    - U / Ctrl+Z: Undo move
    - Y / Ctrl+Y: Redo move
    - H: Reveal smart hint
    - Space / P: Pause / Resume timer
    - R: Quick restart current puzzle
- ⏱️ **Live Timer & Leaderboard Statistics**:
  - Real-time timer with pause/resume overlay.
  - Persistent game statistics (games played, win rates, and fastest solve times per difficulty).
- 🎨 **Luxe Dark Aesthetic**:
  - Luminous cyan and slate accents, glassmorphic cards, peer guides, and victory celebrations.

---

## 📂 Project Structure

`	ext
D:\sudoku-flet│
├── main.py                # Main UI application, responsive views & event handlers
├── game_state.py          # State controller (moves, undo/redo, notes, hints, timer)
├── sudoku_generator.py    # Backtracking puzzle generator, solver & validator
├── test_sudoku.py         # Automated test suite (uniqueness, solver, game mechanics)
├── requirements.txt       # Python dependencies (flet>=1.0.3)
├── .gitignore             # Git ignore configuration
└── README.md              # Project documentation & guides
`

---

## 🚀 Quick Start

### 1. Installation
`powershell
pip install -r requirements.txt
`

### 2. Run as Native Desktop App
`powershell
python main.py
`

### 3. Run as Web / Mobile PWA App
`powershell
python main.py --web
`
*Open http://localhost:8550 on your browser or mobile phone connected to the same Wi-Fi.*

---

## 🧪 Running Tests
`powershell
python test_sudoku.py
`

---

## 📜 License
This project is licensed under the MIT License.
