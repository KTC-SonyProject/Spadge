import logging
import threading

import flet as ft
from flet import (
    Page,
    ScrollMode,
    app,
)

from app.db_conn import DatabaseHandler
from app.logging_config import setup_logging
from app.settings import load_settings
from app.unity_conn import SocketServer
from app.views import MyView


def main(page: Page):
    page.title = "Spadge"
    page.scroll = ScrollMode.AUTO
    page.padding = 10

    server = SocketServer()
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    db = DatabaseHandler(load_settings())
    page.data = {
        "settings_file": "local.settings.json",
        "settings": load_settings,
        "db": db,
        "server": server,
    }

    page.fonts = {
        "default": "/fonts/Noto_Sans_JP/static/NotoSansJP-Regular.ttf",
        "bold": "/fonts/Noto_Sans_JP/static/NotoSansJP-Black.ttf",
    }

    page.window.width = 1000
    page.window.height = 900
    page.window.min_width = 800
    page.window.min_height = 600


    theme = ft.Theme()
    theme.font_family = "default"
    theme.page_transitions.android = ft.PageTransitionTheme.NONE
    theme.page_transitions.ios = ft.PageTransitionTheme.NONE
    theme.page_transitions.macos = ft.PageTransitionTheme.NONE
    theme.page_transitions.linux = ft.PageTransitionTheme.NONE
    theme.page_transitions.windows = ft.PageTransitionTheme.NONE
    page.theme = theme
    page.update()

    MyView(page)

    def on_close():
        server.stop()
        db.close()
        server_thread.join()
        print("Application closed")

    page.on_close = on_close

setup_logging()
logger = logging.getLogger(__name__)
logger.info("app started")
app(target=main, port=8000)
