from flet import (
    Colors,
    Column,
    Container,
    CrossAxisAlignment,
    MainAxisAlignment,
    Page,
    Row,
    Text,
    TextButton,
    alignment,
)


class FooterView(Container):
    def __init__(self, page: Page):
        super().__init__(
            padding=10,
            bgcolor=Colors.SURFACE_CONTAINER_HIGHEST,
            alignment=alignment.center,
        )
        self.page = page
        self.content = Column(
            controls=[
                Row(
                    controls=[
                        TextButton(
                            "Githubプロジェクト",
                            on_click=lambda _: self.page.launch_url(url="https://github.com/KTC-SonyProject"),
                        ),
                        TextButton(
                            "SRDについて",
                            on_click=lambda _: self.page.launch_url(
                                url="https://www.sony.jp/spatial-reality-display/products/ELF-SR2/"
                            ),
                        ),
                        TextButton(
                            "アプリ設計について",
                            on_click=lambda _: self.page.launch_url(
                                url="https://kyoto-tech-sc.notion.site/SPADGE-13fcb359b34a80d4b5b7fe3dda00d6f7?pvs=4"
                            ),
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    spacing=0,
                    wrap=True,
                ),
                Text(
                    value="© 2025 SPADGE",
                    color=Colors.GREY,
                    size=12,
                    text_align="center",
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=10,
        )
