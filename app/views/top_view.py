from flet import (
    Column,
    Container,
    Markdown,
    MarkdownExtensionSet,
    Page,
    ScrollMode,
    app,
)

# カレントディレクトリにあるREADME.mdを取得
md = open("README.md", encoding="utf-8").read()


class TopView(Column):
    def __init__(self, page: Page):
        super().__init__(
            spacing=10,
            expand=True,
            scroll=ScrollMode.AUTO,
        )
        self.controls = [
            Container(
                expand=True,
                content=Markdown(
                    value=md,
                    selectable=True,
                    extension_set=MarkdownExtensionSet.GITHUB_WEB,
                    on_tap_link=lambda e: page.launch_url(e.data),
                ),
            )
        ]


if __name__ == "__main__":

    def main(page: Page) -> None:
        page.title = "test app"
        page.scroll = "auto"
        chat_page = TopView()
        page.add(chat_page)

    app(main)
