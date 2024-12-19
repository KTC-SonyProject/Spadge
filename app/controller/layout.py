import logging

from flet import (
    Page,
    ScrollMode,
    TemplateRoute,
    View,
)

from app.components.chat import ChatBody
from app.controller.home_controller import HomeController
from app.models.route_models import RouteItem, RouteParam, RouteParamKey, RouteParamValue
from app.service_container import Container
from app.views.documents_view import DocumentsView, EditDocumentsView
from app.views.header_view import HeaderView
from app.views.settings_view import SettingsView
from app.views.template_view import TemplateView
from app.views.top_view import TopView
from app.views.unity_view import UnityView
from app.views.voice_view import VoiceView

logger = logging.getLogger(__name__)

ROUTES = {
    "/": RouteItem("Top", TopView),
    "/home": RouteItem("Home", HomeController),
    "/voice": RouteItem("Voice", VoiceView),
    "/documents": RouteItem("Documents", DocumentsView, [
        RouteParam(RouteParamKey.DOCS_MANAGER, RouteParamValue.DOCS_MANAGER)
    ]),
    "/documents/:document_id": RouteItem("Document", DocumentsView, [
        RouteParam(RouteParamKey.DOCS_MANAGER, RouteParamValue.DOCS_MANAGER),
    ]),
    "/documents/:document_id/edit": RouteItem("Edit Document", EditDocumentsView, [
        RouteParam(RouteParamKey.DOCS_MANAGER, RouteParamValue.DOCS_MANAGER),
    ]),
    "/settings": RouteItem("Settings", SettingsView, [
        RouteParam(RouteParamKey.SETTINGS, RouteParamValue.SETTINGS)
    ]),
    "/chat": RouteItem("Chat", ChatBody, [
        RouteParam(RouteParamKey.SERVER, RouteParamValue.SERVER),
    ]),
    "/unity": RouteItem("Unity", UnityView, [
        RouteParam(RouteParamKey.FILE_CONTROLLER, RouteParamValue.FILE_CONTROLLER)
    ]),
    "/404": RouteItem("404 Page Not Found", TemplateView, [
        RouteParam("text", "404 Page Not Found")
    ]),
}


class RoutingHandler:
    def __init__(self, page: Page):
        self.page = page
        self.container = Container.get_instance()

    def resolve_view(self, route: str, extra_params: dict | None = None) -> tuple[str, View]:
        route_info = self._match_dynamic_route(route) or ROUTES.get("/404")
        params = self._resolve_params(route_info.params, route)
        if extra_params:
            params.update(extra_params)
        if route_info.layout == HomeController:
            return route_info.title, route_info.layout(self.page).get_home_view()
        logger.debug(f"Route: {route}")
        return route_info.title, route_info.layout(self.page, **params)

    def _match_dynamic_route(self, route: str):
        for pattern, route_info in ROUTES.items():
            template_route = TemplateRoute(route)
            if template_route.match(pattern):
                if hasattr(template_route, "document_id"):
                    print(f"Document ID: {template_route.document_id}\n\n\n\n")
                    route_info.params.append(RouteParam("document_id", template_route.document_id))
                return route_info
        return None

    def _resolve_params(self, param_list: list[RouteParam] | None, route: str = "/") -> dict:
        params = {}
        if not param_list:
            return params
        for param in param_list:
            # paramのvalueがEnumの場合は、Enumの値を取得する
            logger.debug(f"\n\nParam: {param}\n\n")
            param_value = param.value
            if isinstance(param_value, str) or isinstance(param_value, int):
                params[param.key] = param_value
            elif param_value.value.startswith("data:"):
                param_key = param_value.value.split(":")[1]
                params[param.key.value] = self.container.get(param_key)
            else:
                raise ValueError(f"Invalid param value: {param_value}")
        logger.debug(f"Resolved params: {params}")
        return params




class MyLayout(View):
    def __init__(self, page: Page, route='/'):
        super().__init__(
            route=route,
            scroll=None,
        )
        self.page = page
        # self.expand = True

        # home_controller = HomeController(self.page)


        # スクロールモードを設定しているとエラーが発生するため、チャットページのみスクロールモードを無効にする
        if self.route == '/':
            self.scroll = ScrollMode.AUTO

        self.routing_handler = RoutingHandler(self.page)
        title, layout = self.routing_handler.resolve_view(self.route)

        self.controls = [
            HeaderView(self.page, title.upper()),
            layout,
        ]
        # self.troute = TemplateRoute(self.route)

        # self.route_config = {
        #     "/": {
        #         "title": "Top",
        #         "layout": TopView(self.page),
        #     },
        #     "/home": {
        #         "title": "Home",
        #         "layout": home_controller.get_home_view(),
        #     },
        #     "/voice": {
        #         "title": "Voice",
        #         "layout": VoiceView(self.page),
        #     },
        #     "/documents": {
        #         "title": "Documents",
        #         "layout": DocumentsView(self.page, self.page.data["docs_manager"]),
        #     },
        #     "/settings": {
        #         "title": "Settings",
        #         # 'layout': SettingsBody(self.page),
        #         "layout": SettingsView(self.page, self.page.data["settings"]),
        #     },
        #     "/chat": {
        #         "title": "Chat",
        #         "layout": ChatBody(self.page),
        #     },
        #     "/unity": {
        #         "title": "Unity",
        #         "layout": UnityView(self.page, self.page.data["file_controller"]),
        #     },
        # }

        # self.default_route_config = {
        #     "title": "404 Page Not Found",
        #     "layout": TemplateView(self.page, "404 Page Not Found"),
        # }

        # if self.troute.match("/documents/:document_id"):
        #     self.route_info = {
        #         'title': 'Document',
        #         'layout': DocumentsView(self.page, self.page.data['docs_manager'], self.troute.document_id),
        #     }
        #     logger.debug(f"Document ID: {self.troute.document_id}")
        # elif self.troute.match("/documents/:document_id/edit"):
        #     self.route_info = {
        #         "title": "Edit Document",
        #         "layout": EditDocumentsView(self.page, self.page.data["docs_manager"], self.troute.document_id),
        #     }
        #     logger.debug(f"Edit Document ID: {self.troute.document_id}")
        # else:
        #     self.route_info = self.route_config.get(self.route, self.default_route_config)
        #     logger.debug(f"Route: {self.route}")

        # self.controls = [
        #     HeaderView(self.page, self.route_info["title"].upper()),
        #     self.route_info["layout"],  # ルートごとに適切なレイアウトを取得
        # ]
