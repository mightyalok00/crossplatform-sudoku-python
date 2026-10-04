"""
Modern Sudoku Game with Flet.
Playable on Desktop, Web, and Mobile with responsive touch/mouse controls,
number entry, mistake feedback, pencil notes, solver hints, and difficulty modes.
"""

import argparse
import asyncio
from collections.abc import Sequence

import flet as ft
from sudoku_flow.core.game import SudokuGame
from sudoku_flow.storage import StatisticsStore, default_stats
from sudoku_flow.ui.theme import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BORDER_BOX,
    COLOR_BORDER_CELL,
    COLOR_CELL_BG,
    COLOR_ERROR_BG,
    COLOR_ERROR_TEXT,
    COLOR_GIVEN_TEXT,
    COLOR_MATCH_BG,
    COLOR_NOTE_TEXT,
    COLOR_PEER_BG,
    COLOR_SELECTED_BG,
    COLOR_SUCCESS,
    COLOR_SURFACE,
    COLOR_SURFACE_LIGHT,
    COLOR_USER_TEXT,
)

def format_time(seconds: int) -> str:
    if seconds is None:
        return "--:--"
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"

def main(page: ft.Page):
    page.title = "Sudoku Flow"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_BG
    page.padding = 8
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Game state & persistent stats
    game = SudokuGame(difficulty="Medium")
    stats = default_stats()
    statistics_store = StatisticsStore()

    async def restore_stats() -> None:
        """Hydrate the in-memory view after Flet storage becomes available."""
        stats.clear()
        stats.update(await statistics_store.load())

    def persist_stats() -> None:
        """Save an immutable snapshot without delaying user interactions."""
        snapshot = {section: values.copy() for section, values in stats.items()}

        async def save_snapshot() -> None:
            await statistics_store.save(snapshot)

        page.run_task(save_snapshot)

    # UI References
    timer_text = ft.Text("00:00", size=17, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT)
    mistakes_text = ft.Text("Mistakes: 0/3", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE_70)
    difficulty_badge = ft.Text("MEDIUM", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT)

    cell_containers: list[list[ft.Container]] = [[None for _ in range(9)] for _ in range(9)]
    keypad_buttons: dict[int, ft.Container] = {}
    keypad_counts: dict[int, ft.Text] = {}

    # ---------------- Timer Background Loop ----------------
    async def timer_loop():
        while True:
            await asyncio.sleep(1)
            if not game.is_paused and not game.is_won and not game.is_game_over:
                game.elapsed_seconds += 1
                timer_text.value = format_time(game.elapsed_seconds)
                page.update()

    # ---------------- Cell Visual Styling ----------------
    def get_cell_styling(r: int, c: int):
        val = game.current_grid[r][c]
        is_selected = (game.selected_cell == (r, c))
        sel_r, sel_c = game.selected_cell if game.selected_cell else (-1, -1)
        sel_val = game.current_grid[sel_r][sel_c] if (sel_r >= 0 and sel_c >= 0) else 0

        is_peer = False
        if sel_r >= 0 and sel_c >= 0:
            same_row = (r == sel_r)
            same_col = (c == sel_c)
            same_box = (r // 3 == sel_r // 3) and (c // 3 == sel_c // 3)
            is_peer = same_row or same_col or same_box

        is_match = (val != 0 and sel_val != 0 and val == sel_val)

        # Conflict / Mistake check
        is_mistake = False
        if val != 0 and not game.is_given(r, c) and val != game.solution_grid[r][c]:
            is_mistake = True

        # Background
        if is_selected:
            bg_color = COLOR_SELECTED_BG
        elif is_mistake:
            bg_color = COLOR_ERROR_BG
        elif is_match:
            bg_color = COLOR_MATCH_BG
        elif is_peer:
            bg_color = COLOR_PEER_BG
        else:
            bg_color = COLOR_CELL_BG

        # Borders
        top_w = 2.0 if r % 3 == 0 else 0.8
        top_c = COLOR_BORDER_BOX if r % 3 == 0 else COLOR_BORDER_CELL
        left_w = 2.0 if c % 3 == 0 else 0.8
        left_c = COLOR_BORDER_BOX if c % 3 == 0 else COLOR_BORDER_CELL
        bot_w = 2.0 if r == 8 else 0.8
        bot_c = COLOR_BORDER_BOX if r == 8 else COLOR_BORDER_CELL
        right_w = 2.0 if c == 8 else 0.8
        right_c = COLOR_BORDER_BOX if c == 8 else COLOR_BORDER_CELL

        if is_selected:
            border = ft.Border(
                top=ft.BorderSide(2.5, COLOR_ACCENT),
                left=ft.BorderSide(2.5, COLOR_ACCENT),
                bottom=ft.BorderSide(2.5, COLOR_ACCENT),
                right=ft.BorderSide(2.5, COLOR_ACCENT)
            )
        else:
            border = ft.Border(
                top=ft.BorderSide(top_w, top_c),
                left=ft.BorderSide(left_w, left_c),
                bottom=ft.BorderSide(bot_w, bot_c),
                right=ft.BorderSide(right_w, right_c)
            )

        return bg_color, border, is_mistake

    def build_cell_content(r: int, c: int, is_mistake: bool):
        val = game.current_grid[r][c]
        if val != 0:
            if game.is_given(r, c):
                text_color = COLOR_GIVEN_TEXT
                font_weight = ft.FontWeight.W_800
            elif is_mistake:
                text_color = COLOR_ERROR_TEXT
                font_weight = ft.FontWeight.BOLD
            else:
                text_color = COLOR_USER_TEXT
                font_weight = ft.FontWeight.BOLD

            return ft.Container(alignment=ft.Alignment.CENTER,
                content=ft.Text(
                    str(val),
                    size=20,
                    weight=font_weight,
                    color=text_color,
                )
            )
        else:
            # Notes / Pencil Marks
            notes = game.notes_grid[r][c]
            if not notes:
                return ft.Container()

            note_rows = []
            for nr in range(3):
                note_cols = []
                for nc in range(3):
                    n_val = nr * 3 + nc + 1
                    txt = str(n_val) if n_val in notes else ""
                    note_cols.append(
                        ft.Container(
                            content=ft.Text(txt, size=8, weight=ft.FontWeight.BOLD, color=COLOR_NOTE_TEXT),
                            alignment=ft.Alignment.CENTER,
                            expand=True,
                        )
                    )
                note_rows.append(ft.Row(controls=note_cols, expand=True, spacing=0))

            return ft.Column(controls=note_rows, expand=True, spacing=0)

    def refresh_cell(r: int, c: int):
        bg, border, is_mistake = get_cell_styling(r, c)
        cell = cell_containers[r][c]
        cell.bgcolor = bg
        cell.border = border
        cell.content = build_cell_content(r, c, is_mistake)

    def update_entire_board():
        # Update mistake counter
        if game.strict_mistakes:
            mistakes_text.value = f"Mistakes: {game.mistakes_count}/{game.max_mistakes}"
            mistakes_text.color = COLOR_ERROR_TEXT if game.mistakes_count > 0 else ft.Colors.WHITE_70
        else:
            mistakes_text.value = f"Mistakes: {game.mistakes_count}"
            mistakes_text.color = ft.Colors.WHITE_70

        # Update difficulty badge
        difficulty_badge.value = game.difficulty.upper()

        # Update Notes Button active visual state
        notes_btn.bgcolor = COLOR_ACCENT if game.notes_mode else COLOR_SURFACE_LIGHT
        notes_btn.content.controls[0].color = ft.Colors.BLACK if game.notes_mode else ft.Colors.WHITE
        notes_btn.content.controls[1].color = ft.Colors.BLACK if game.notes_mode else ft.Colors.WHITE_70

        # Update remaining counts for each number
        counts = game.get_number_counts()
        for num in range(1, 10):
            remaining = max(0, 9 - counts[num])
            keypad_counts[num].value = str(remaining)
            if remaining == 0:
                keypad_buttons[num].opacity = 0.25
                keypad_counts[num].color = ft.Colors.WHITE_24
            else:
                keypad_buttons[num].opacity = 1.0
                keypad_counts[num].color = COLOR_ACCENT

        # Refresh all 81 cells
        for r in range(9):
            for c in range(9):
                refresh_cell(r, c)

        page.update()

        # Check for game end conditions
        if game.is_game_over:
            show_game_over_dialog()
        elif game.is_won:
            handle_victory()

    # ---------------- Interaction Handlers ----------------
    def on_cell_click(e, r: int, c: int):
        if game.is_paused or game.is_game_over or game.is_won:
            return
        game.select_cell(r, c)
        update_entire_board()

    def handle_number_input(num: int):
        if game.is_paused or game.is_game_over or game.is_won:
            return
        game.enter_number(num)
        update_entire_board()

    def handle_erase(e=None):
        if game.is_paused or game.is_game_over or game.is_won:
            return
        if game.erase_selected():
            update_entire_board()

    def handle_undo(e=None):
        if game.is_paused or game.is_game_over or game.is_won:
            return
        if game.undo():
            update_entire_board()

    def handle_redo(e=None):
        if game.is_paused or game.is_game_over or game.is_won:
            return
        if game.redo():
            update_entire_board()

    def handle_notes_toggle(e=None):
        game.toggle_notes_mode()
        update_entire_board()

    def handle_hint(e=None):
        if game.is_paused or game.is_game_over or game.is_won:
            return
        res = game.use_hint()
        if res:
            update_entire_board()
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(f"💡 Hint placed at Row {res[0]+1}, Col {res[1]+1}!", color=ft.Colors.WHITE),
                    bgcolor="#0284C7",
                    duration=1500
                )
            )

    def toggle_pause(e=None):
        if game.is_won or game.is_game_over:
            return
        game.is_paused = not game.is_paused
        pause_btn.icon = ft.Icons.PLAY_ARROW_ROUNDED if game.is_paused else ft.Icons.PAUSE_ROUNDED
        pause_overlay.visible = game.is_paused
        page.update()

    # ---------------- Keyboard Events ----------------
    def on_keyboard_event(e: ft.KeyboardEvent):
        key = e.key
        if game.is_paused and key.lower() != 'p':
            return

        r, c = game.selected_cell if game.selected_cell else (0, 0)

        if key in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            handle_number_input(int(key))
        elif key in ["Backspace", "Delete", "0"]:
            handle_erase()
        elif key in ["ArrowUp", "w", "W"]:
            game.select_cell(max(0, r - 1), c)
            update_entire_board()
        elif key in ["ArrowDown", "s", "S"]:
            game.select_cell(min(8, r + 1), c)
            update_entire_board()
        elif key in ["ArrowLeft", "a", "A"]:
            game.select_cell(r, max(0, c - 1))
            update_entire_board()
        elif key in ["ArrowRight", "d", "D"]:
            game.select_cell(r, min(8, c + 1))
            update_entire_board()
        elif key.lower() == "n":
            handle_notes_toggle()
        elif key.lower() == "u" or (e.ctrl and key.lower() == "z"):
            handle_undo()
        elif key.lower() == "y" or (e.ctrl and key.lower() == "y"):
            handle_redo()
        elif key.lower() == "h":
            handle_hint()
        elif key.lower() == "p" or key == " ":
            toggle_pause()

    page.on_keyboard_event = on_keyboard_event

    # ---------------- Modals & Dialogs ----------------
    def handle_victory():
        # Record stats
        diff = game.difficulty
        stats["won"][diff] = stats["won"].get(diff, 0) + 1
        curr_best = stats["best_time"].get(diff)
        if curr_best is None or game.elapsed_seconds < curr_best:
            stats["best_time"][diff] = game.elapsed_seconds
        persist_stats()
        show_win_dialog()

    def show_game_over_dialog():
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color=COLOR_ERROR_TEXT, size=28),
                ft.Text("Game Over", weight=ft.FontWeight.BOLD, color=COLOR_ERROR_TEXT, size=22)
            ], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Column([
                ft.Text(f"You made {game.max_mistakes} mistakes and lost this game.", size=14, color=ft.Colors.WHITE_70, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Difficulty: {game.difficulty} | Time: {format_time(game.elapsed_seconds)}", size=13, color=COLOR_NOTE_TEXT, text_align=ft.TextAlign.CENTER),
            ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Restart Puzzle", on_click=lambda e: restart_confirmed(dlg)),
                ft.FilledButton("New Puzzle", style=ft.ButtonStyle(bgcolor=COLOR_ACCENT, color=ft.Colors.BLACK), on_click=lambda e: new_game_from_dlg(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=COLOR_SURFACE,
        )
        page.show_dialog(dlg)

    def show_win_dialog():
        diff = game.difficulty
        best_t = stats["best_time"].get(diff)
        is_new_record = (best_t == game.elapsed_seconds)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EMOJI_EVENTS_ROUNDED, color=COLOR_SUCCESS, size=32),
                ft.Text("Puzzle Solved!", weight=ft.FontWeight.BOLD, color=COLOR_SUCCESS, size=22)
            ], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Column([
                ft.Text("🌟 Congratulations! 🌟", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                ft.Container(height=4),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("Difficulty:", color=COLOR_NOTE_TEXT), ft.Text(game.difficulty, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("Time:", color=COLOR_NOTE_TEXT), ft.Text(f"{format_time(game.elapsed_seconds)} {'🏆 (New Best!)' if is_new_record else ''}", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("Mistakes:", color=COLOR_NOTE_TEXT), ft.Text(str(game.mistakes_count), weight=ft.FontWeight.BOLD, color=COLOR_ERROR_TEXT if game.mistakes_count > 0 else COLOR_SUCCESS)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("Hints Used:", color=COLOR_NOTE_TEXT), ft.Text(str(game.hints_used), weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=6),
                    bgcolor=COLOR_CELL_BG,
                    padding=12,
                    border_radius=10,
                )
            ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.FilledButton("Play Next Game", style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS, color=ft.Colors.BLACK), on_click=lambda e: new_game_from_dlg(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor=COLOR_SURFACE,
        )
        page.show_dialog(dlg)

    def restart_confirmed(dlg=None):
        if dlg:
            page.pop_dialog()
        game.restart_current_game()
        update_entire_board()

    def new_game_from_dlg(dlg=None):
        if dlg:
            page.pop_dialog()
        start_new_puzzle(game.difficulty)

    def start_new_puzzle(difficulty: str):
        stats["played"][difficulty] = stats["played"].get(difficulty, 0) + 1
        persist_stats()
        game.start_new_game(difficulty)
        timer_text.value = "00:00"
        pause_btn.icon = ft.Icons.PAUSE_ROUNDED
        pause_overlay.visible = False
        update_entire_board()

    def open_difficulty_picker(e):
        def choose_diff(diff):
            page.pop_dialog()
            start_new_puzzle(diff)

        diff_dlg = ft.AlertDialog(
            title=ft.Text("Choose Difficulty", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.ListTile(leading=ft.Icon(ft.Icons.LOOKS_ONE_ROUNDED, color=COLOR_SUCCESS), title=ft.Text("Easy (40 clues)"), on_click=lambda e: choose_diff("Easy")),
                ft.ListTile(leading=ft.Icon(ft.Icons.LOOKS_TWO_ROUNDED, color=COLOR_ACCENT), title=ft.Text("Medium (32 clues)"), on_click=lambda e: choose_diff("Medium")),
                ft.ListTile(leading=ft.Icon(ft.Icons.LOOKS_3_ROUNDED, color=ft.Colors.AMBER), title=ft.Text("Hard (26 clues)"), on_click=lambda e: choose_diff("Hard")),
                ft.ListTile(leading=ft.Icon(ft.Icons.LOOKS_4_ROUNDED, color=COLOR_ERROR_TEXT), title=ft.Text("Expert (22 clues)"), on_click=lambda e: choose_diff("Expert")),
            ], tight=True),
            bgcolor=COLOR_SURFACE,
        )
        page.show_dialog(diff_dlg)

    def open_statistics_dialog(e):
        stat_rows = []
        for d in ["Easy", "Medium", "Hard", "Expert"]:
            pl = stats["played"].get(d, 0)
            wn = stats["won"].get(d, 0)
            bt = format_time(stats["best_time"].get(d))
            stat_rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(d, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT, width=70),
                        ft.Text(f"Played: {pl}", size=12, color=ft.Colors.WHITE_70, width=75),
                        ft.Text(f"Won: {wn}", size=12, color=COLOR_SUCCESS, width=65),
                        ft.Text(f"Best: {bt}", size=12, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.symmetric(vertical=4),
                )
            )

        stat_dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.LEADERBOARD_ROUNDED, color=COLOR_ACCENT),
                ft.Text("Statistics", weight=ft.FontWeight.BOLD)
            ], spacing=8),
            content=ft.Column(stat_rows, tight=True),
            actions=[ft.TextButton("Close", on_click=lambda e: page.pop_dialog())],
            bgcolor=COLOR_SURFACE,
        )
        page.show_dialog(stat_dlg)

    def open_settings_dialog(e):
        def toggle_strict(e_val):
            game.strict_mistakes = e_val.control.value
            update_entire_board()

        def toggle_auto_notes(e_val):
            game.auto_clear_notes = e_val.control.value

        sett_dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.SETTINGS_ROUNDED, color=COLOR_ACCENT),
                ft.Text("Settings", weight=ft.FontWeight.BOLD)
            ], spacing=8),
            content=ft.Column([
                ft.Switch(label="Mistake Limit (3 Max)", value=game.strict_mistakes, active_color=COLOR_ACCENT, on_change=toggle_strict),
                ft.Switch(label="Auto-clear Notes on Entry", value=game.auto_clear_notes, active_color=COLOR_ACCENT, on_change=toggle_auto_notes),
            ], tight=True),
            actions=[ft.TextButton("Done", on_click=lambda e: page.pop_dialog())],
            bgcolor=COLOR_SURFACE,
        )
        page.show_dialog(sett_dlg)

    # ---------------- Top App Bar & Status Header ----------------
    pause_btn = ft.IconButton(
        icon=ft.Icons.PAUSE_ROUNDED,
        icon_color=COLOR_ACCENT,
        tooltip="Pause / Resume (Space / P)",
        on_click=toggle_pause
    )

    top_header = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.GRID_4X4_ROUNDED, color=COLOR_ACCENT, size=26),
                ft.Text("SUDOKU", size=19, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE, style=ft.TextStyle(letter_spacing=1.5)),
            ], spacing=8),
            ft.Row([
                ft.IconButton(icon=ft.Icons.LEADERBOARD_OUTLINED, icon_color=ft.Colors.WHITE_70, tooltip="Game Statistics", on_click=open_statistics_dialog),
                ft.IconButton(icon=ft.Icons.REFRESH_ROUNDED, icon_color=ft.Colors.WHITE_70, tooltip="Restart Current Puzzle", on_click=lambda e: restart_confirmed()),
                ft.IconButton(icon=ft.Icons.SETTINGS_OUTLINED, icon_color=ft.Colors.WHITE_70, tooltip="Settings", on_click=open_settings_dialog),
            ], spacing=0)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding.symmetric(horizontal=4, vertical=2)
    )

    status_bar = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Row([
                    difficulty_badge,
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=COLOR_ACCENT, size=18)
                ], spacing=2),
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=20,
                bgcolor=COLOR_SURFACE_LIGHT,
                on_click=open_difficulty_picker,
                tooltip="Change Difficulty",
                ink=True
            ),
            ft.Row([
                ft.Icon(ft.Icons.TIMER_OUTLINED, color=COLOR_ACCENT, size=18),
                timer_text,
                pause_btn
            ], spacing=4),
            mistakes_text,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=12,
        bgcolor=COLOR_SURFACE,
    )

    # ---------------- 9x9 Board Layout ----------------
    board_grid_rows = []
    for r in range(9):
        row_cells = []
        for c in range(9):
            cell_box = ft.Container(
                width=40,
                height=40,
                alignment=ft.Alignment.CENTER,
                border_radius=4,
                animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
                on_click=lambda e, row=r, col=c: on_cell_click(e, row, col),
                ink=True
            )
            cell_containers[r][c] = cell_box
            row_cells.append(cell_box)
        board_grid_rows.append(ft.Row(controls=row_cells, spacing=0, alignment=ft.MainAxisAlignment.CENTER))

    board_container = ft.Container(
        content=ft.Column(controls=board_grid_rows, spacing=0, alignment=ft.MainAxisAlignment.CENTER),
        padding=6,
        border_radius=14,
        bgcolor=COLOR_SURFACE,
        border=ft.Border.all(2, COLOR_BORDER_BOX),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=16,
            color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
            offset=ft.Offset(0, 4)
        ),
        alignment=ft.Alignment.CENTER
    )

    # Pause Overlay Screen
    pause_overlay = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.PAUSE_CIRCLE_FILLED_ROUNDED, size=60, color=COLOR_ACCENT),
            ft.Text("Game Paused", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=8),
            ft.FilledButton("Resume", style=ft.ButtonStyle(bgcolor=COLOR_ACCENT, color=ft.Colors.BLACK), on_click=toggle_pause)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.with_opacity(0.92, COLOR_BG),
        border_radius=14,
        visible=False,
        alignment=ft.Alignment.CENTER,
        expand=True
    )

    board_stack = ft.Stack([
        board_container,
        pause_overlay
    ], alignment=ft.Alignment.CENTER)

    # ---------------- Tool Actions Bar ----------------
    def make_action_btn(icon, label, on_click, tooltip):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                ft.Text(label, size=11, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE_70)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            border_radius=10,
            bgcolor=COLOR_SURFACE_LIGHT,
            on_click=on_click,
            tooltip=tooltip,
            ink=True
        )

    notes_btn = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=20, color=ft.Colors.WHITE),
            ft.Text("Notes", size=11, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE_70)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        padding=ft.Padding.symmetric(horizontal=12, vertical=6),
        border_radius=10,
        bgcolor=COLOR_SURFACE_LIGHT,
        on_click=handle_notes_toggle,
        tooltip="Toggle Pencil Notes Mode (N)",
        ink=True
    )

    action_bar = ft.Row([
        make_action_btn(ft.Icons.UNDO_ROUNDED, "Undo", handle_undo, "Undo Move (U / Ctrl+Z)"),
        make_action_btn(ft.Icons.REDO_ROUNDED, "Redo", handle_redo, "Redo Move (Y / Ctrl+Y)"),
        make_action_btn(ft.Icons.BACKSPACE_OUTLINED, "Erase", handle_erase, "Erase Cell (Backspace/Del)"),
        notes_btn,
        make_action_btn(ft.Icons.LIGHTBULB_ROUNDED, "Hint", handle_hint, "Get Hint (H)"),
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

    # ---------------- Number Keypad (1 - 9) ----------------
    keypad_row = []
    for num in range(1, 10):
        cnt_text = ft.Text("9", size=10, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT)
        keypad_counts[num] = cnt_text

        btn = ft.Container(
            content=ft.Column([
                ft.Text(str(num), size=19, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                cnt_text
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            width=42,
            height=50,
            border_radius=8,
            bgcolor=COLOR_SURFACE,
            border=ft.Border.all(1, COLOR_BORDER_BOX),
            on_click=lambda e, n=num: handle_number_input(n),
            ink=True,
            tooltip=f"Input {num} (Press {num})"
        )
        keypad_buttons[num] = btn
        keypad_row.append(btn)

    keypad_container = ft.Row(controls=keypad_row, spacing=3, alignment=ft.MainAxisAlignment.CENTER)

    # ---------------- Bottom Controls ----------------
    bottom_bar = ft.Row([
        ft.FilledButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, size=18),
                ft.Text("New Puzzle", weight=ft.FontWeight.BOLD, size=13)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            style=ft.ButtonStyle(bgcolor=COLOR_ACCENT, color=ft.Colors.BLACK),
            on_click=open_difficulty_picker,
            expand=True
        )
    ], alignment=ft.MainAxisAlignment.CENTER)

    # ---------------- Main Page Assembly ----------------
    main_column = ft.Column([
        top_header,
        status_bar,
        ft.Container(height=2),
        board_stack,
        ft.Container(height=4),
        action_bar,
        ft.Container(height=2),
        keypad_container,
        ft.Container(height=4),
        bottom_bar
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, tight=True)

    app_card = ft.Container(
        content=main_column,
        width=420,
        alignment=ft.Alignment.CENTER
    )

    page.add(app_card)
    update_entire_board()

    # Start timer loop
    page.run_task(timer_loop)
    page.run_task(restore_stats)

def run(argv: Sequence[str] | None = None) -> None:
    """Launch Sudoku Flow as a desktop or browser application."""
    parser = argparse.ArgumentParser(description="Launch the Sudoku Flow game.")
    parser.add_argument(
        "--web",
        action="store_true",
        help="open the game in a browser on port 8550",
    )
    args = parser.parse_args(argv)

    if args.web:
        print("Starting Sudoku Pro in Web/Mobile Browser mode on port 8550...")
        ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
    else:
        ft.run(main)


if __name__ == "__main__":
    run()
