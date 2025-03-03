import atexit
import logging
import os

from flet import (
    Colors,
    Page,
    PageTransitionTheme,
    ScrollMode,
    Theme,
    app,
)

from app.controller import (
    AuthManager,
    DocumentsManager,
    FileManager,
    ObjectDatabaseManager,
    ObjectManager,
    ServerManager,
    SettingsManager,
)
from app.logging_config import setup_logging
from app.models.database_models import DatabaseHandler
from app.service_container import Container
from app.views.views import MyView

server = ServerManager()


def server_clean_up():
    server.stop()


def initialize_services(page: Page) -> Container:
    """必要なサービスを初期化してコンテナに登録"""
    container = Container.get_instance()

    # 各サービスの初期化
    settings_manager = SettingsManager()
    db_handler = DatabaseHandler(settings_manager)
    obj_database_manager = ObjectDatabaseManager(db_handler)
    obj_manager = ObjectManager(obj_database_manager, server)
    docs_manager = DocumentsManager(db_handler)
    file_manager = FileManager(page, server, obj_database_manager, obj_manager)
    auth_manager = AuthManager(page)

    # コンテナに登録
    container.register("settings_manager", settings_manager)
    container.register("db_handler", db_handler)
    container.register("obj_database_manager", obj_database_manager)
    container.register("obj_manager", obj_manager)
    container.register("docs_manager", docs_manager)
    container.register("socket_server", server)
    container.register("file_manager", file_manager)
    container.register("auth_manager", auth_manager)

    return container


def main(page: Page):
    page.title = "SPADGE"
    page.scroll = ScrollMode.AUTO

    initialize_services(page)

    page.data = {
        "settings_file": "local.settings.json",
    }

    page.fonts = {
        "default": "/fonts/Noto_Sans_JP/static/NotoSansJP-Regular.ttf",
        "bold": "/fonts/Noto_Sans_JP/static/NotoSansJP-Black.ttf",
        "icon-camar": "/fonts/camar/Camar.otf",
        "icon-term": "/fonts/term/Term.ttf",
        "icon-stentiga": "/fonts/stentiga/Stentiga.ttf",
    }

    page.window.width = 1000
    page.window.height = 900
    page.window.min_width = 800
    page.window.min_height = 600

    theme = Theme(color_scheme_seed=Colors.GREY)
    theme.font_family = "default"
    theme.page_transitions.android = PageTransitionTheme.NONE
    theme.page_transitions.ios = PageTransitionTheme.NONE
    theme.page_transitions.macos = PageTransitionTheme.NONE
    theme.page_transitions.linux = PageTransitionTheme.NONE
    theme.page_transitions.windows = PageTransitionTheme.NONE
    page.theme = theme
    page.update()

    MyView(page)

    def on_close():
        server.stop()
        # container.get("db_handler").close_connection()
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
    server.start()  # ServerManagerがスレッドを内部で管理
    atexit.register(server_clean_up)
    app(target=main, port=8000, assets_dir="assets", upload_dir="storage/temp/uploads")
except KeyboardInterrupt:
    logger.info("App stopped by user")
except OSError as e:
    logger.error(f"Port is already in use or invalid: {e}")
except Exception as e:
    logger.error(f"Error starting app: {e}")
finally:
    # logger.info("App stopped")
    # container = Container.get_instance()
    # container.get("db_handler").close_connection()
    server.stop()
    server.thread.join(timeout=3)
    logging.shutdown()
