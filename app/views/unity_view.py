import logging

from flet import (
    Column,
    Container,
    ElevatedButton,
    FilePicker,
    ListView,
    MainAxisAlignment,
    Row,
    Text,
    alignment,
)

from app.views.core import BaseTabBodyView, TabView, create_tabs

logger = logging.getLogger(__name__)


class BaseUnityTabView(BaseTabBodyView):
    def __init__(self, title: str, body_content: any):
        super().__init__(title, body_content)


def create_obj_list_view(show_obj: callable, delete_obj: callable, obj_list: list[str] | None = None) -> ListView:
    lv = ListView(
        expand=1,
        spacing=10,
        padding=20,
    )
    if obj_list is None:
        lv = ListView(
            controls=[
                Text("Unityと接続されていないか、オブジェクトがありません", size=15),
            ]
        )
    else:
        for obj in obj_list:
            lv.controls.append(
                Row(
                    controls=[
                        Text(obj, size=15),
                        ElevatedButton(
                            text="表示",
                            on_click=lambda _, obj=obj: show_obj(obj),
                        ),
                        ElevatedButton(
                            text="削除",
                            on_click=lambda _, obj=obj: delete_obj(obj),
                        ),
                    ]
                )
            )
    return lv


class ObjListView(Column):
    def __init__(self, get_obj_list: callable):
        super().__init__(
            controls=[
                Row(
                    [
                        Text("Upload object 一覧", size=20),
                        ElevatedButton(
                            text="リストを更新する",
                            on_click=lambda _: self.update_obj_list(),
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                create_obj_list_view(self.show_obj, self.delete_obj, get_obj_list()),
            ],
            expand=True,
        )
        self.get_obj_list = get_obj_list

    def update_obj_list(self):
        self.controls[1] = create_obj_list_view(self.show_obj, self.delete_obj, self.get_obj_list())

    def show_obj(self, obj: str):
        logger.info(f"Show {obj}")

    def delete_obj(self, obj: str):
        logger.info(f"Delete {obj}")


def create_display_settings_body() -> Column:
    return ObjListView()


def create_file_settings_body(
    file_picker: FilePicker,
    selected_files: Text,
    upload_button: ElevatedButton,
) -> Column:
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
                            allowed_extensions=["obj", "mtl", "jpg", "txt", "ply"],  # ファイル拡張子の指定(デバッグ用)
                        ),
                    ),
                    ElevatedButton(
                        text="zipファイルの場合",
                        on_click=lambda _: file_picker.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["zip"],
                        ),
                    ),
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
