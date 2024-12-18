import logging

from flet import (
    Page,
    ScrollMode,
    TemplateRoute,
    View,
)

from app.components.chat import ChatBody
from app.views.documents_view import DocumentsView, EditDocumentsView
from app.views.header_view import HeaderView
from app.views.home_view import HomeView
from app.views.settings_view import SettingsView
from app.views.template_view import TemplateView
from app.views.top_view import TopView
from app.views.unity_view import UnityView
from app.views.voice_view import VoiceView

logger = logging.getLogger(__name__)

class MyLayout(View):
    def __init__(self, page: Page, route='/'):
        super().__init__()
        self.page = page
        self.route = route
        self.expand = True
        self.scroll = None

        # スクロールモードを設定しているとエラーが発生するため、チャットページのみスクロールモードを無効にする
        if self.route == '/':
            self.scroll = ScrollMode.AUTO

        self.troute = TemplateRoute(self.route)

        self.route_config = {
            "/": {
                "title": "Top",
                "layout": TopView(self.page),
            },
            "/home": {
                "title": "Home",
                "layout": HomeView(self.page),
            },
            "/voice": {
                "title": "Voice",
                "layout": VoiceView(self.page),
            },
            "/documents": {
                "title": "Documents",
                "layout": DocumentsView(self.page, self.page.data["docs_manager"]),
            },
            "/settings": {
                "title": "Settings",
                # 'layout': SettingsBody(self.page),
                "layout": SettingsView(self.page, self.page.data["settings"]),
            },
            "/chat": {
                "title": "Chat",
                "layout": ChatBody(self.page),
            },
            "/unity": {
                "title": "Unity",
                "layout": UnityView(self.page, self.page.data["file_controller"]),
            },
        }

        self.default_route_config = {
            "title": "404 Page Not Found",
            "layout": TemplateView(self.page, "404 Page Not Found"),
        }

        if self.troute.match("/documents/:document_id"):
            self.route_info = {
                'title': 'Document',
                'layout': DocumentsView(self.page, self.page.data['docs_manager'], self.troute.document_id),
            }
            logger.debug(f"Document ID: {self.troute.document_id}")
        elif self.troute.match("/documents/:document_id/edit"):
            self.route_info = {
                "title": "Edit Document",
                "layout": EditDocumentsView(self.page, self.page.data["docs_manager"], self.troute.document_id),
            }
            logger.debug(f"Edit Document ID: {self.troute.document_id}")
        else:
            self.route_info = self.route_config.get(self.route, self.default_route_config)
            logger.debug(f"Route: {self.route}")

        self.controls = [
            HeaderView(self.page, self.route_info["title"].upper()),
            self.route_info["layout"],  # ルートごとに適切なレイアウトを取得
        ]
