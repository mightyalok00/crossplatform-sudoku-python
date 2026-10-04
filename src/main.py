import logging

import flet as ft

from storage import load_game
from views.game_screen import SudokuScreen

LOG_LEVEL = logging.INFO
logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("app").setLevel(LOG_LEVEL)
log = logging.getLogger("app.main")


async def main(page: ft.Page):
    page.title = "Sudoku"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.CYAN_300,
        scaffold_bgcolor=ft.Colors.BLUE_GREY_900,
        card_bgcolor=ft.Colors.BLUE_GREY_800,
    )
    page.bgcolor = ft.Colors.BLUE_GREY_900
    page.padding = 12
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    preferences = ft.SharedPreferences()
    state = await load_game(preferences)
    if state:
        log.info("Resuming saved %s Sudoku game", state["difficulty"])

    screen = SudokuScreen(page, preferences, state)
    page.add(screen.build())
    screen.start_clock()


ft.run(main)
