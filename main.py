"""Convenience launcher for running the project directly from a checkout."""

from pathlib import Path
import sys

SOURCE_DIRECTORY = Path(__file__).parent / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

from sudoku_flow.app import run


if __name__ == "__main__":
    run()
