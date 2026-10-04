# 🎯 Sudoku Flow

<p align="center">
  <strong>A modern, responsive Sudoku game built with Python and Flet.</strong><br>
  Play on the web, desktop, or mobile with hints, notes, timers, statistics, and smart puzzle generation.
</p>

<p align="center">
  <a href="https://sudokualok.netlify.app/"><img src="https://img.shields.io/badge/🎮%20Play%20Live-Netlify-00C7B7?style=for-the-badge" alt="Play Sudoku Flow"></a>
  <a href="https://mightyalok00.github.io/crossplatform-sudoku-python/"><img src="https://img.shields.io/badge/🌐%20GitHub%20Pages-Live-222222?style=for-the-badge&logo=github" alt="GitHub Pages"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Flet-1.0%2B-0EA5E9?style=flat-square&logo=flutter&logoColor=white" alt="Flet">
  <img src="https://img.shields.io/badge/Platform-Web%20%7C%20Desktop%20%7C%20Mobile-10B981?style=flat-square" alt="Platforms">
  <img src="https://img.shields.io/github/actions/workflow/status/mightyalok00/crossplatform-sudoku-python/tests.yml?branch=main&style=flat-square&label=tests" alt="Tests">
</p>

> **Sudoku Flow** is a cross-platform Sudoku experience focused on clean UI, responsive gameplay, reliable puzzle logic, and persistent player statistics.

---

## 🚀 Live Demo

### ⭐ Play Now

**[🎮 Open Sudoku Flow on Netlify](https://sudokualok.netlify.app/)**

You can also use the GitHub Pages deployment:

**[🌐 Open Sudoku Flow on GitHub Pages](https://mightyalok00.github.io/crossplatform-sudoku-python/)**

No installation is required for the web version.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧩 **Sudoku Generator** | Generates puzzles designed around unique solutions |
| 🎚️ **Difficulty Levels** | Easy, Medium, Hard, and Expert difficulty targets |
| ✏️ **Pencil Notes** | Track candidate numbers while solving |
| 💡 **Hints** | Get assistance when you are stuck |
| ↩️ **Undo / Redo** | Safely step backward and forward through moves |
| ❌ **Mistake Tracking** | Keep track of incorrect entries |
| ⏱️ **Timer** | Track solving time during each game |
| 📊 **Statistics** | Save and review player statistics locally |
| 💾 **Persistent Storage** | Flet client storage keeps data between sessions |
| 📱 **Responsive UI** | Designed for web, desktop, and mobile experiences |
| 🌐 **Web Deployment** | Automated GitHub Pages deployment through GitHub Actions |

---

## 🧠 How It Works

Sudoku Flow separates the application into clear layers:

~~~~text
┌─────────────────────────────────────────────┐
│                  Flet UI                    │
│        Board • Controls • Theme • UX        │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│               Game State                    │
│       Moves • Notes • Timer • Mistakes      │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│            Sudoku Core Engine               │
│    Generation • Solving • Validation        │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│             Local Storage                   │
│       Statistics • Player Progress          │
└─────────────────────────────────────────────┘
~~~~

The architecture keeps Sudoku logic independent from the interface, making the project easier to test, maintain, and extend.

---

## 🗂️ Project Structure

~~~~text
crossplatform-sudoku-python/
│
├── src/
│   └── sudoku_flow/
│       ├── app.py                 # Flet application and interactions
│       ├── storage.py             # Local statistics persistence
│       ├── core/
│       │   ├── engine.py          # Generator, solver, validation
│       │   ├── game.py            # Game state and moves
│       │   └── web_puzzles.py     # Fast randomized web puzzles
│       └── ui/
│           └── theme.py           # Shared UI/theme tokens
│
├── tests/                         # Unit tests
├── .github/
│   └── workflows/                # CI and deployment workflows
├── main.py                        # Checkout-friendly launcher
├── pyproject.toml                 # Project metadata and dependencies
├── requirements.txt               # Compatibility installer
└── README.md
~~~~

---

## ⚡ Quick Start

### 1. Clone the repository

~~~~powershell
git clone https://github.com/mightyalok00/crossplatform-sudoku-python.git
cd crossplatform-sudoku-python
~~~~

### 2. Create a virtual environment

~~~~powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
~~~~

### 3. Install the project

~~~~powershell
python -m pip install -e .
~~~~

### 4. Start Sudoku Flow

**Desktop:**

~~~~powershell
python main.py
~~~~

**Web:**

~~~~powershell
python main.py --web
~~~~

You can also use the installed command:

~~~~powershell
sudoku-flow
~~~~

---

## 🧪 Testing

Run the complete unit-test suite with:

~~~~powershell
python -m unittest discover -s tests -v
~~~~

The test suite covers the core game behaviour and storage functionality.

---

## 🎮 Difficulty System

Sudoku Flow uses clue targets to create progressively harder puzzles:

| Difficulty | Target clues |
|---|---:|
| 🟢 Easy | 40 |
| 🟡 Medium | 32 |
| 🟠 Hard | 26 |
| 🔴 Expert | 22 |

The generator may retain additional clues when required to preserve a unique solution.

---

## 💾 Data & Storage

Player statistics are persisted using Flet client storage:

- 🌐 **Web:** browser local storage
- 💻 **Desktop:** local JSON-backed storage
- 📱 **Mobile:** platform preference storage

This allows statistics and player data to remain available between sessions without requiring a remote database.

---

## ☁️ Deployment

The project includes GitHub Actions automation for building and deploying the web application.

### GitHub Pages

Pushes to `main` trigger the web build and deployment workflow.

**Production URL:**  
https://mightyalok00.github.io/crossplatform-sudoku-python/

### Netlify

A public Netlify deployment is also available:

**Production URL:**  
https://sudokualok.netlify.app/

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| 🐍 **Python** | Application and Sudoku logic |
| ⚡ **Flet** | Cross-platform UI |
| 🧩 **Python unittest** | Automated testing |
| 💾 **Flet Client Storage** | Local persistence |
| 🤖 **GitHub Actions** | CI and deployment |
| 🌍 **GitHub Pages / Netlify** | Web hosting |

---

## 📌 Project Highlights

This project demonstrates practical software-development concepts including:

- Object-oriented Python application design
- Sudoku generation and solving algorithms
- Game-state management
- Input validation and conflict detection
- Persistent local storage
- Responsive cross-platform UI development
- Automated testing
- Continuous deployment
- Production web hosting

---

## 🗺️ Roadmap

- [x] Cross-platform Flet application
- [x] Multiple difficulty levels
- [x] Puzzle generation and validation
- [x] Hints and pencil notes
- [x] Undo / redo
- [x] Timer and mistake tracking
- [x] Persistent statistics
- [x] Web deployment
- [ ] Online leaderboard
- [ ] Daily Sudoku challenge
- [ ] User profiles
- [ ] Additional themes

---

## 🤝 Contributing

Contributions and ideas are welcome.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Open a pull request

Please keep changes focused and include tests when adding or changing core game logic.

---

## 👨‍💻 Author

**Alok Agarwal**

- GitHub: [@mightyalok00](https://github.com/mightyalok00)
- Repository: [crossplatform-sudoku-python](https://github.com/mightyalok00/crossplatform-sudoku-python)

---

## 📄 License

This repository currently does not include a license file. Add an appropriate open-source license before distributing or reusing the project under specific licensing terms.

---

<p align="center">
  <strong>🎮 Play Sudoku Flow → <a href="https://sudokualok.netlify.app/">sudokualok.netlify.app</a></strong>
</p>

<p align="center">
  Built with ❤️ using Python + Flet
</p>
