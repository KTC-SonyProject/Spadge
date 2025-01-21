import logging

from flet import (
    Column,
    Container,
    ElevatedButton,
    FilePicker,
    Row,
    Text,
    alignment,
)

from app.views.core import BaseTabBodyView, TabView, create_tabs

logger = logging.getLogger(__name__)


class BaseUnityTabView(BaseTabBodyView):
    def __init__(self, title: str, body_content: any):
        super().__init__(title, body_content)


def create_display_settings_body():
    return Column(
        controls=[Text("Display Settings")],
    )


def create_file_settings_body(
    file_picker: FilePicker,
    selected_files: Text,
    upload_button: ElevatedButton,
):
    return Column(
        alignment=alignment.center,
        expand=True,
        controls=[
            Row(
                [
                    ElevatedButton(
                        text="ファイルを選択",
                        # on_click=lambda _: file_picker.pick_files(allowed_extensions=["txt", "pdf", "obj", "ply"]),
                        on_click=lambda _: file_picker.pick_files(
                            allow_multiple=True,
                            allowed_extensions=["obj", "mtl", "jpg", "txt", "ply"], # ファイル拡張子の指定(デバッグ用)
                        ),
                    ),
                    ElevatedButton(
                        text="zipファイルの場合",
                        on_click=lambda _: file_picker.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["zip"],
                        ),
                    )
                ]
            ),
            selected_files,
            upload_button,
        ],
    )


class UnityView(Column):
    def __init__(self, tabs: list[TabView]):
        super().__init__(
            spacing=10,
            expand=True,
        )

        title = Container(
            padding=10,
            alignment=alignment.center,
            content=Row(
                spacing=20,
                controls=[
                    Text("Unity Application", size=30),
                ],
            ),
        )

        self.controls = [
            title,
            create_tabs(tabs),
        ]
