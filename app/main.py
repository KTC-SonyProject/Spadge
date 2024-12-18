import logging
import os
import threading

import flet as ft
from flet import (
    Page,
    ScrollMode,
    app,
)

from app.controller.documents_manager import DocumentsManager
from app.controller.file_controller import FileController
from app.controller.settings_manager import SettingsManager
from app.logging_config import setup_logging
from app.models.database_models import DatabaseHandler
from app.unity_conn import SocketServer
from app.views.views import MyView

server = SocketServer()
server_thread = threading.Thread(target=server.start, daemon=True)
server_thread.start()

def main(page: Page):
    page.title = "Spadge"
    page.scroll = ScrollMode.AUTO
    page.padding = 10

    settings_manager = SettingsManager()
    db_handler = DatabaseHandler(settings_manager)
    docs_manager = DocumentsManager(db_handler)
    file_controller = FileController(page, server)

    page.data = {
        "settings_file": "local.settings.json",
        "settings": settings_manager,
        "db": db_handler,
        "docs_manager": docs_manager,
        "server": server,
        "file_controller": file_controller,
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
        db_handler.close()
        server_thread.join()
        print("Application closed")

    page.on_close = on_close

setup_logging()
logger = logging.getLogger(__name__)
logger.info("app started")

# ファイルのアップロード用のシークレットキーを環境変数から取得
if not os.environ.get("FLET_SECRET_KEY"):
    logger.warning("FLET_SECRET is not set.")
    os.environ["FLET_SECRET_KEY"] = "secret"

try:
    app(target=main, port=8000, assets_dir="assets", upload_dir="storage/temp/uploads")
except KeyboardInterrupt:
    logger.info("App stopped by user")
    server.stop()
    server_thread.join()
    raise
except OSError:
    logger.error("Port is already in use")
    server.stop()
    server_thread.join()
    # もう一度tryする
except Exception as e:
    logger.error(f"Error starting app: {e}")
    raise e
