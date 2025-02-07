import socket

from flet import (
    AppBar,
    Colors,
    Container,
    IconButton,
    Icons,
    Image,
    ImageFit,
    MainAxisAlignment,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    Row,
    Text,
)
from app.controller.manager.auth_manager import AuthManager


class HeaderView(AppBar):
    def __init__(self, page: Page, page_title: str = "Example"):
        super().__init__()
        self.page = page
        self.page_title = page_title
        self.auth_manager = AuthManager(page)
        self.is_authenticated = self.auth_manager.check_is_authenticated()

        self.toggle_dark_light_icon = IconButton(
            icon=Icons.LIGHT_MODE_OUTLINED if self.page.theme_mode == "light" else Icons.DARK_MODE_OUTLINED,
            tooltip="switch light and dark mode",
            on_click=self.toggle_icon,
        )
        self.chat_icon = IconButton(
            icon=Icons.CHAT_BUBBLE_OUTLINE,
            tooltip="Chat",
            on_click=lambda _: self.page.go("/chat"),
        )
        self.appbar_items = [
            PopupMenuItem(text="Top", on_click=lambda _: self.page.go("/")),
            PopupMenuItem(text="Home", on_click=lambda _: self.page.go("/home")),
            PopupMenuItem(),
            PopupMenuItem(text="Chat", on_click=lambda _: self.page.go("/chat")),
            PopupMenuItem(text="Documents", on_click=lambda _: self.page.go("/documents")),
            PopupMenuItem(text="Unity App", on_click=lambda _: self.page.go("/unity")),
            PopupMenuItem(),
        ]
        if self.is_authenticated:
            self.appbar_items.append(PopupMenuItem(text="Settings", on_click=lambda _: self.page.go("/settings")))
            self.appbar_items.append(PopupMenuItem(text="Logout", on_click=lambda _: self.page.go("/logout")))
        else:
            self.appbar_items.append(PopupMenuItem(text="Login", on_click=lambda _: self.page.go("/login")))
        self.leading = IconButton(
            content=Image(
                src="icon.png",
                width=75,
                height=75,
                fit=ImageFit.COVER,
            ),
            on_click=lambda _: self.page.go("/"),
        )
        self.leading_width = 75
        self.title = Text(
            value=self.page_title, size=30, font_family="icon-camar", no_wrap=True, color=Colors.BLUE_GREY
        )
        self.center_title = False
        self.toolbar_height = 75
        self.bgcolor = Colors.SURFACE_CONTAINER_HIGHEST
        self.actions = [
            Container(
                # margin=margin.only(left=50, right=25),
                content=Row(
                    alignment=MainAxisAlignment.END,
                    spacing=0,
                    controls=[
                        # Text("IP: " + self.get_opc_ip(), size=10),
                        self.chat_icon,
                        self.toggle_dark_light_icon,
                        PopupMenuButton(items=self.appbar_items),
                    ],
                ),
            )
        ]

    def toggle_icon(self, e):
        # テーマモードを切り替え
        self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"
        # アイコンを切り替え
        self.toggle_dark_light_icon.icon = (
            Icons.LIGHT_MODE_OUTLINED if self.page.theme_mode == "light" else Icons.DARK_MODE_OUTLINED
        )
        # ページを更新
        self.page.update()

    # 動作しているOPCのIPアドレスを取得
    def get_opc_ip(self):
        host_ip = socket.gethostbyname("host.docker.internal")
        return host_ip


if __name__ == "__main__":
    import flet as ft

    def main(page: ft.Page) -> None:
        page.title = "AI Chat"
        example = HeaderView(page)
        page.add(example)

    ft.app(main)
