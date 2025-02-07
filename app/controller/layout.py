import logging

from flet import (
    Column,
    Page,
    TemplateRoute,
    View,
)

from app.controller import (
    ChatController,
    DocumentsController,
    HomeController,
    SettingsController,
    UnityController,
)
from app.controller.auth_controller import AuthController
from app.models.route_models import RouteItem, RouteParam, RouteParamKey, RouteParamValue
from app.service_container import Container
from app.views.footer_view import FooterView
from app.views.header_view import HeaderView
from app.views.template_view import TemplateView
from app.views.top_view import TopView
from app.views.voice_view import VoiceView

logger = logging.getLogger(__name__)

ROUTES = {
    "/": RouteItem("Top", TopView),
    "/home": RouteItem("Home", HomeController),
    "/voice": RouteItem("Voice", VoiceView),
    "/documents": RouteItem(
        "Documents", DocumentsController, [RouteParam(RouteParamKey.DOCS_MANAGER, RouteParamValue.DOCS_MANAGER)]
    ),
    "/documents/:document_id": RouteItem(
        "Document",
        DocumentsController,
        [RouteParam(RouteParamKey.DOCS_MANAGER, RouteParamValue.DOCS_MANAGER)],
    ),
    "/documents/:document_id/edit": RouteItem(
        "Edit Document",
        DocumentsController,
        [
            RouteParam(RouteParamKey.DOCS_MANAGER, RouteParamValue.DOCS_MANAGER),
            RouteParam("is_edit", True),
        ],
    ),
    "/login": RouteItem(
        "Login", AuthController, [RouteParam(RouteParamKey.AUTH_MANAGER, RouteParamValue.AUTH_MANAGER)]
    ),
    "/settings": RouteItem(
        "Settings",
        SettingsController,
        [
            RouteParam(RouteParamKey.SETTINGS, RouteParamValue.SETTINGS),
            RouteParam(RouteParamKey.AUTH_MANAGER, RouteParamValue.AUTH_MANAGER),
        ],
    ),
    "/chat": RouteItem(
        "Chat",
        ChatController,
        [RouteParam(RouteParamKey.SERVER, RouteParamValue.SERVER)],
    ),
    "/unity": RouteItem(
        "Unity",
        UnityController,
        [
            RouteParam(RouteParamKey.FILE_MANAGER, RouteParamValue.FILE_MANAGER),
            RouteParam(RouteParamKey.SERVER, RouteParamValue.SERVER),
        ],
    ),
    "/404": RouteItem("404 Page Not Found", TemplateView, [RouteParam("text", "404 Page Not Found")]),
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
        if route_info.layout in {
            HomeController,
            SettingsController,
            DocumentsController,
            UnityController,
            ChatController,
            AuthController,
        }:
            return route_info.title, route_info.layout(self.page, **params).get_view()
        logger.debug(f"Route: {route}")
        return route_info.title, route_info.layout(self.page, **params)

    def _match_dynamic_route(self, route: str):
        for pattern, route_info in ROUTES.items():
            template_route = TemplateRoute(route)
            if template_route.match(pattern):
                if hasattr(template_route, "document_id"):
                    route_info.params.append(RouteParam("document_id", template_route.document_id))
                return route_info
        return None

    def _resolve_params(self, param_list: list[RouteParam] | None, route: str = "/") -> dict:
        params = {}
        if not param_list:
            return params
        for param in param_list:
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
    def __init__(self, page: Page, route="/"):
        super().__init__(
            route=route,
            scroll=None,
            spacing=0,
            padding=0,
        )

        self.routing_handler = RoutingHandler(page)
        title, layout = self.routing_handler.resolve_view(self.route)
        # layoutにFooterViewを追加
        # layoutにcontrols属性がない場合はColumnにする
        if not hasattr(layout, "controls"):
            layout = Column(
                controls=[layout, FooterView(page)],
                expand=True,
            )
        else:
            layout.controls.append(FooterView(page))

        self.controls = [
            HeaderView(page, title.upper()),
            layout,
            # FooterView(page),
        ]
