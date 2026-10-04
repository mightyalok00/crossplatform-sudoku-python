"""Flet interface for the Sudoku game."""

from __future__ import annotations

import asyncio
import logging

import flet as ft

from game import conflicts, new_game, next_hint, solved
from storage import save_game

log = logging.getLogger("app.views.game_screen")


class SudokuScreen:
    def __init__(self, page: ft.Page, preferences, state: dict | None):
        self._page = page
        self._preferences = preferences
        self.state = state or new_game()
        self._status_message = "Your saved game is ready." if state else "Choose a square, then tap a number."
        self._cell_size = max(29, min(42, (float(page.width or 420) - 24) / 9))
        self._board_holder = ft.Container()
        self._timer_text = ft.Text(size=18, color=ft.Colors.CYAN_200, weight=ft.FontWeight.BOLD)
        self._status_text = ft.Text(size=14, color=ft.Colors.BLUE_GREY_200, text_align=ft.TextAlign.CENTER)
        self._progress_text = ft.Text(size=13, color=ft.Colors.BLUE_GREY_300)
        self._difficulty = ft.Dropdown(
            value=self.state["difficulty"],
            options=[ft.DropdownOption(key=level, text=level.title()) for level in ("easy", "medium", "hard")],
            on_select=self._difficulty_changed,
            width=132,
            dense=True,
            filled=True,
            fill_color=ft.Colors.BLUE_GREY_800,
            border_color=ft.Colors.BLUE_GREY_600,
            focused_border_color=ft.Colors.CYAN_300,
            text_size=14,
        )
        self._number_holder = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self._root = None

    def build(self):
        self._board_holder.content = self._build_board()
        self._number_holder.controls = self._build_number_pad()
        self._refresh_labels()

        header = ft.Column(
            tight=True,
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("SUDOKU", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_200),
                ft.Text("A little logic goes a long way", size=13, color=ft.Colors.BLUE_GREY_300),
            ],
        )
        toolbar = ft.Row(
            tight=True,
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self._difficulty,
                ft.Button(
                    content=ft.Text("New game"),
                    on_click=self._new_game,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.CYAN_800, color=ft.Colors.WHITE),
                ),
            ],
        )
        actions = ft.Row(
            tight=True,
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Button(
                    content=ft.Text("Hint"),
                    on_click=self._hint,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.CYAN_100),
                ),
                ft.Button(
                    content=ft.Text("Erase"),
                    on_click=self._erase,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.BLUE_GREY_100),
                ),
            ],
        )
        self._root = ft.Column(
            tight=True,
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                header,
                ft.Row(
                    tight=True,
                    spacing=18,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Row(tight=True, spacing=5, controls=[ft.Text("◷", size=19, color=ft.Colors.CYAN_200), self._timer_text]),
                        self._progress_text,
                    ],
                ),
                self._board_holder,
                self._status_text,
                self._number_holder,
                toolbar,
                actions,
                ft.Text("Progress saves automatically on this device.", size=12, color=ft.Colors.BLUE_GREY_400),
            ],
        )
        return self._root

    def start_clock(self):
        asyncio.create_task(self._clock())

    async def _clock(self):
        while True:
            await asyncio.sleep(1)
            if not solved(self.state):
                self.state["elapsed"] += 1
                self._timer_text.value = self._format_time(self.state["elapsed"])
                self._timer_text.update()
                if self.state["elapsed"] % 5 == 0:
                    await save_game(self._preferences, self.state)

    @staticmethod
    def _format_time(seconds: int) -> str:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"

    def _build_board(self):
        bad_cells = conflicts(self.state["board"])
        selected_row, selected_col = self.state.get("selected", [0, 0])
        selected_value = self.state["board"][selected_row][selected_col]
        size = self._cell_size
        rows = []
        for row in range(9):
            cells = []
            for col in range(9):
                value = self.state["board"][row][col]
                fixed = self.state["puzzle"][row][col] != 0
                selected = (row, col) == (selected_row, selected_col)
                same_number = bool(selected_value and value == selected_value)
                peer = row == selected_row or col == selected_col or (row // 3, col // 3) == (selected_row // 3, selected_col // 3)
                if (row, col) in bad_cells:
                    background = ft.Colors.RED_900
                    text_color = ft.Colors.RED_100
                elif selected:
                    background = ft.Colors.CYAN_800
                    text_color = ft.Colors.WHITE
                elif same_number:
                    background = ft.Colors.CYAN_900
                    text_color = ft.Colors.CYAN_100
                elif peer:
                    background = ft.Colors.BLUE_GREY_700
                    text_color = ft.Colors.WHITE if fixed else ft.Colors.CYAN_200
                else:
                    background = ft.Colors.BLUE_GREY_800
                    text_color = ft.Colors.BLUE_GREY_100 if fixed else ft.Colors.CYAN_200

                line_color = ft.Colors.BLUE_GREY_500
                cell = ft.Container(
                    width=size,
                    height=size,
                    alignment=ft.Alignment.CENTER,
                    bgcolor=background,
                    border=ft.Border(
                        top=ft.BorderSide(width=2 if row % 3 == 0 else 1, color=line_color),
                        right=ft.BorderSide(width=2 if col % 3 == 2 else 1, color=line_color),
                        bottom=ft.BorderSide(width=1, color=line_color),
                        left=ft.BorderSide(width=2 if col % 3 == 0 else 1, color=line_color),
                    ),
                    ink=True,
                    on_click=self._select_handler(row, col),
                    content=ft.Text(
                        str(value) if value else "",
                        size=max(16, size * 0.48),
                        weight=ft.FontWeight.BOLD if fixed else ft.FontWeight.NORMAL,
                        color=text_color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                )
                cells.append(cell)
            rows.append(ft.Row(tight=True, spacing=0, controls=cells))
        return ft.Column(tight=True, spacing=0, controls=rows)

    def _build_number_pad(self):
        rows = []
        for values in (range(1, 6), range(6, 10)):
            keys = []
            for number in values:
                remaining = 9 - sum(row.count(number) for row in self.state["board"])
                keys.append(
                    ft.Container(
                        width=max(34, self._cell_size),
                        height=42,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=ft.Colors.BLUE_GREY_800 if remaining else ft.Colors.BLUE_GREY_900,
                        border=ft.Border.all(1, ft.Colors.BLUE_GREY_600),
                        border_radius=8,
                        ink=bool(remaining),
                        on_click=self._number_handler(number) if remaining else None,
                        content=ft.Column(
                            tight=True,
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(str(number), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_100 if remaining else ft.Colors.BLUE_GREY_500),
                                ft.Text(str(remaining), size=9, color=ft.Colors.BLUE_GREY_300),
                            ],
                        ),
                    )
                )
            rows.append(ft.Row(tight=True, spacing=7, alignment=ft.MainAxisAlignment.CENTER, controls=keys))
        return rows

    def _refresh_labels(self):
        self._timer_text.value = self._format_time(self.state["elapsed"])
        filled = sum(value != 0 for row in self.state["board"] for value in row)
        self._progress_text.value = f"{filled}/81 filled  ·  {self.state.get('hints', 0)} hints"
        if solved(self.state):
            self._status_message = "Puzzle complete — beautifully solved!"
            self._status_text.color = ft.Colors.GREEN_300
        self._status_text.value = self._status_message

    def _refresh(self):
        self._board_holder.content = self._build_board()
        self._number_holder.controls = self._build_number_pad()
        self._refresh_labels()
        self._page.update()

    async def _persist(self):
        await save_game(self._preferences, self.state)

    def _select_handler(self, row: int, col: int):
        def handler():
            self._select_cell(row, col)

        return handler

    def _number_handler(self, number: int):
        async def handler():
            await self._enter_number(number)

        return handler

    def _select_cell(self, row: int, col: int):
        self.state["selected"] = [row, col]
        self._status_message = "Select a square, then tap a number."
        self._refresh()

    async def _enter_number(self, number: int):
        row, col = self.state.get("selected", [0, 0])
        if self.state["puzzle"][row][col] != 0:
            self._status_message = "That square is part of the original puzzle. Choose an empty square."
            self._refresh()
            return
        if solved(self.state):
            return
        self.state["board"][row][col] = number
        self._status_message = "Repeated numbers are highlighted in red." if conflicts(self.state["board"]) else ""
        self._refresh()
        await self._persist()

    async def _erase(self):
        row, col = self.state.get("selected", [0, 0])
        if self.state["puzzle"][row][col] == 0:
            self.state["board"][row][col] = 0
            self._status_message = "Square cleared."
            self._refresh()
            await self._persist()
        else:
            self._status_message = "Original puzzle squares cannot be erased."
            self._refresh()

    async def _hint(self):
        if solved(self.state):
            return
        cell = next_hint(self.state)
        if cell is None:
            return
        row, col = cell
        self.state["selected"] = [row, col]
        self.state["board"][row][col] = self.state["solution"][row][col]
        self.state["hints"] = self.state.get("hints", 0) + 1
        self._status_message = "One correct number revealed."
        self._refresh()
        await self._persist()

    async def _difficulty_changed(self, event):
        self.state = new_game(event.control.value or "medium")
        self._status_message = f"New {self.state['difficulty']} puzzle started."
        self._refresh()
        await self._persist()

    async def _new_game(self):
        self.state = new_game(self.state["difficulty"])
        self._status_message = f"New {self.state['difficulty']} puzzle started."
        self._difficulty.value = self.state["difficulty"]
        self._refresh()
        await self._persist()
