import socket

# from flet import (
#     AppBar,
#     Colors,
#     Container,
#     Icon,
#     IconButton,
#     Icons,
#     MainAxisAlignment,
#     Page,
#     PopupMenuButton,
#     PopupMenuItem,
#     Row,
#     Text,
#     margin,
#     Image,
#     ImageFit,
# )

import socket
from flet import (
    AppBar,
    Colors,
    Container,
    Icon,
    IconButton,
    Icons,
    MainAxisAlignment,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    Row,
    Text,
    margin,
    Image,
    ImageFit,
)

# class HeaderView(Container):
#     def __init__(self, page: Page, page_title: str = "Example"):
#         super().__init__(
#             height=75,
#             bgcolor=Colors.SURFACE_CONTAINER_HIGHEST,
#         )
#         self.page = page
#         self.page_title = page_title
        
#         # ライト/ダークモード切替用のアイコンボタン
#         self.toggle_dark_light_icon = IconButton(
#             icon=Icons.LIGHT_MODE_OUTLINED if self.page.theme_mode == "light" else Icons.DARK_MODE_OUTLINED,
#             tooltip="switch light and dark mode",
#             on_click=self.toggle_icon,
#         )
#         # チャット用アイコンボタン
#         self.chat_icon = IconButton(
#             icon=Icons.CHAT_BUBBLE_OUTLINE,
#             tooltip="Chat",
#             on_click=lambda _: self.page.go("/chat"),
#         )
#         # ポップアップメニューのアイテム群
#         self.appbar_items = [
#             PopupMenuItem(text="Top", on_click=lambda _: self.page.go("/")),
#             PopupMenuItem(text="Home", on_click=lambda _: self.page.go("/home")),
#             PopupMenuItem(),
#             PopupMenuItem(text="Chat", on_click=lambda _: self.page.go("/chat")),
#             PopupMenuItem(text="Documents", on_click=lambda _: self.page.go("/documents")),
#             PopupMenuItem(text="Unity App", on_click=lambda _: self.page.go("/unity")),
#             PopupMenuItem(),
#             PopupMenuItem(text="Settings", on_click=lambda _: self.page.go("/settings")),
#         ]
#         # 先頭のアイコン
#         self.leading = IconButton(
#             content=Image(
#                 src="icon.png",
#                 width=50,
#                 height=50,
#                 fit=ImageFit.CONTAIN,
#             ),
#             on_click=lambda _: self.page.go("/"),
#         )
#         # タイトルテキスト（内容・フォントサイズ・配置は変更していない）
#         self.title_text = Text(value=self.page_title, size=30)
#         # 右側のアクション部分
#         self.actions = [
#             Container(
#                 margin=margin.only(left=50, right=25),
#                 content=Row(
#                     alignment=MainAxisAlignment.SPACE_BETWEEN,
#                     controls=[
#                         Text("IP: " + self.get_opc_ip(), size=10),
#                         self.chat_icon,
#                         self.toggle_dark_light_icon,
#                         PopupMenuButton(items=self.appbar_items),
#                     ],
#                 ),
#             )
#         ]
#         # ヘッダー内のレイアウトをRowで構成する
#         self.content = Row(
#             controls=[
#                 # 先頭のアイコン部分（固定幅60）
#                 Container(
#                     width=50,
#                     content=Row(
#                         controls=[
#                         self.leading,
#                         self.title_text,
#                         ]
#                     )
#                 ),
#                 # 右側のアクション部分
#                 Row(controls=self.actions, spacing=10),
#             ],
#             alignment=MainAxisAlignment.SPACE_BETWEEN,
#             vertical_alignment="center",
#         )
    
#     def toggle_icon(self, e):
#         # テーマモードを切り替え、対応するアイコンに更新する
#         self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"
#         self.toggle_dark_light_icon.icon = (
#             Icons.LIGHT_MODE_OUTLINED if self.page.theme_mode == "light" else Icons.DARK_MODE_OUTLINED
#         )
#         self.page.update()
    
#     def get_opc_ip(self):
#         # 動作中のOPCのIPアドレスを取得する（host.docker.internalを利用）
#         host_ip = socket.gethostbyname("host.docker.internal")
#         return host_ip



class HeaderView(AppBar):
    def __init__(self, page: Page, page_title: str = "Example"):
        super().__init__()
        self.page = page
        self.page_title = page_title
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
            PopupMenuItem(text="Settings", on_click=lambda _: self.page.go("/settings")),
        ]
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
        self.title = Text(value=self.page_title, size=30, text_align="center")
        self.center_title = False
        self.toolbar_height = 75
        self.bgcolor = Colors.SURFACE_CONTAINER_HIGHEST
        self.actions = [
            Container(
                margin=margin.only(left=50, right=25),
                content=Row(
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        Text("IP: " + self.get_opc_ip(), size=10),
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
