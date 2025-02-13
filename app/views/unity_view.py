import logging

from flet import (
    Card,
    Colors,
    Column,
    Container,
    CrossAxisAlignment,
    Divider,
    ElevatedButton,
    FilePicker,
    Icon,
    ListView,
    MainAxisAlignment,
    Page,
    Row,
    Text,
    TextField,
    alignment,
)

from app.views.core import BaseTabBodyView, TabView, create_modal, create_tabs

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
    def __init__(
        self,
        get_obj_list: callable,
        show_obj: callable,
    ):
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
                create_obj_list_view(show_obj, self.delete_obj, get_obj_list()),
            ],
            expand=True,
        )
        self.get_obj_list = get_obj_list
        self.show_obj = show_obj

    def update_obj_list(self):
        self.controls[1] = create_obj_list_view(self.show_obj, self.delete_obj, self.get_obj_list())

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


class OldUnityView(Column):
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


# ------------------------新旧の境目------------------------


def create_btn(text: str, on_click: callable, icon: Icon | None = None, visible: bool = True) -> ElevatedButton:
    return ElevatedButton(
        text=text, bgcolor=Colors.BLUE, color=Colors.WHITE, on_click=on_click, icon=icon, visible=visible
    )


def create_update_model_modal(content: TextField, yes_func: callable, no_func: callable) -> Container:
    return create_modal(
        title=Text("モデル変更"),
        content=content,
        actions=[
            create_btn("変更", yes_func),
            create_btn("キャンセル", no_func),
        ],
    )


def create_add_model_modal(content: TextField, yes_func: callable, no_func: callable) -> Container:
    return create_modal(
        title=Text("モデル追加"),
        content=content,
        actions=[
            create_btn("追加", yes_func),
            create_btn("キャンセル", no_func),
        ],
    )


class ModelView(Card):
    """
    3DモデルのView

    Args:
        model_name (str): モデル名
        show_obj (callable): モデル表示関数
        update_obj_name (callable): モデル名変更関数
        delete_obj (callable): モデル削除関数

    ## Attributes:
        model_name (Text): モデル名
        btn_show (ElevatedButton): モデル表示ボタン
        btn_rename (ElevatedButton): モデル名変更ボタン
        btn_delete (ElevatedButton): モデル削除ボタン
        model_row (Row): モデル操作ボタンのRow

    Examples:
        >>> model_view = ModelView("Model A")
        >>> model_view.model_name.value = "Model B" # モデル名を変更
    """

    def __init__(
        self,
        model_name: str,
        show_obj: callable,
        update_obj_name: callable,
        delete_obj: callable,
        is_authenticated: bool = False,
    ):
        super().__init__()
        self.model_name = Text(model_name, size=20, weight="bold", color=Colors.GREY_600)
        self.btn_show = create_btn("👁️ 表示", show_obj)
        self.btn_rename = create_btn("✏️ 名前変更", update_obj_name)  # FIXME: visible=is_authenticatedを一時的に解除中
        self.btn_delete = create_btn("🗑️ 削除", delete_obj)  # FIXME: visible=is_authenticatedを一時的に解除中
        self.model_row = Row(
            controls=[self.btn_show, self.btn_rename, self.btn_delete],
            spacing=10,
            alignment=MainAxisAlignment.CENTER,
            wrap=True,
            expand=True,
        )

        self.content = Container(
            content=Column(
                controls=[
                    self.model_name,
                    self.model_row,
                ],
                spacing=10,
            ),
            padding=15,
            bgcolor=Colors.GREY_300,
            border_radius=10,
        )


class ModelUploadView(Container):
    """モデルアップロードをおこなうボタンのView"""

    def __init__(self, upload_model: callable, file_picker: FilePicker, is_authenticated: bool = False):
        super().__init__()  # FIXME: visible=is_authenticatedを一時的に解除中
        self.file_picker = file_picker
        self.add_model_file_name = Text("", size=16)
        btn_select_model = create_btn(
            "＋ モデル追加", lambda _: self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["zip"])
        )
        self.add_model_name = TextField(hint_text="モデル名を入力", visible=False)
        self.btn_upload_model = create_btn("📤 モデルアップロード", on_click=upload_model, visible=False)
        self.content = Column(
            controls=[
                btn_select_model,
                Row([self.add_model_file_name, self.add_model_name], spacing=10),
                self.btn_upload_model,
            ],
        )


class UnityView(Container):
    """
    Unity操作画面のView

    Args:
        page (Page): ページ
        model_list (list[ModelView]): モデルリスト
        select_model (callable): モデルセレクト関数
        upload_model (callable): モデルアップロード関数
        refresh_list (callable): リスト更新関数
        refresh_status (callable): 接続状況更新関数
        show_current_obj (callable): 現在のオブジェクト表示関数
        rotate_start (callable): モデル回転開始関数
        rotate_stop (callable): モデル回転停止関数

    ## Attributes:
        page_title (Container): ページタイトル
        status_controls (Row): 接続状況コントロール
        model_list_view (Row): モデルリスト
        global_controls (Row): グローバルコントロール
        content (Column): コンテンツ

    Examples:
        >>> import flet as ft
        >>>
        >>> def dammy_func():
        ...     pass
        >>>
        >>> def main(page: Page):
        ...     page.add(UnityView(
        ...         page,
        ...         [
        ...             ModelView("Model A", dammy_func, dammy_func, dammy_func),
        ...             ModelView("Model B", dammy_func, dammy_func, dammy_func),
        ...             ModelView("Model C", dammy_func, dammy_func, dammy_func),
        ...         ],
        ...         dammy_func,
        ...         dammy_func,
        ...         dammy_func,
        ...         dammy_func,
        ...         dammy_func,
        ...         dammy_func,
        ...     ))
        >>>
        >>> ft.app(target=main)
    """

    def __init__(  # noqa
        self,
        page: Page,
        model_list: list[ModelView | Text],
        model_upload_view: ModelUploadView,
        refresh_list: callable,
        unity_status: Text,
        refresh_status: callable,
        rotate_start: callable,
        rotate_stop: callable,
        show_current_obj_name: str = None,
        is_authenticated: bool = False,
    ):
        super().__init__(
            expand=True,
            padding=20,
        )
        self.page = page
        self.model_list = model_list
        self.unity_status = unity_status
        self.show_current_object = Text('ステータスを更新してください', size=25)
        self.show_current_object_row = Row(
            controls=[self.show_current_object, create_btn("🔄 ステータス更新", lambda _: refresh_status("current_obj_name"))],
            spacing=10,
            alignment=MainAxisAlignment.CENTER,
            vertical_alignment=CrossAxisAlignment.CENTER,
        )
        btn_ask_model = create_btn("❓ モデルについて質問する", lambda _: self.page.go("/chat"))
        btn_refresh_list = create_btn("🔄 リストの更新", lambda _: refresh_list("model_list"))
        btn_refresh_status = create_btn("🔄 接続状況の更新", lambda _: refresh_status("unity_status"))
        btn_rotate_start = create_btn("🔄 モデル回転スタート", lambda _: rotate_start())
        btn_rotate_stop = create_btn("⏹ モデル回転ストップ", lambda _: rotate_stop())
        rotation_buttons = Container(
            content=Column(
                controls=[
                    Divider(),
                    self.show_current_object_row,
                    Row(controls=[btn_rotate_start, btn_rotate_stop], spacing=10, alignment=MainAxisAlignment.CENTER),
                ],
                spacing=20,
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
            ),
            padding=50,
        )

        self.page_title = Container(
            content=Text("ディスプレイ 操作ページ", size=35, weight="bold"),
            alignment=alignment.center,
            padding=20,
        )
        self.status_controls = Row(
            controls=[self.unity_status, btn_refresh_status],
            spacing=15,
            alignment=MainAxisAlignment.END,
        )
        self.model_list_view = Row(
            controls=self.model_list,
            spacing=10,
            alignment=MainAxisAlignment.START,
            vertical_alignment=CrossAxisAlignment.CENTER,
            wrap=True,
        )
        self.global_controls = Column(
            controls=[
                self.status_controls,
                btn_ask_model,
                rotation_buttons,
            ],
            spacing=15,
            alignment=MainAxisAlignment.END,
            horizontal_alignment=CrossAxisAlignment.END,
        )
        self.content = Column(
            controls=[
                self.page_title,
                self.global_controls,
                self.model_list_view,
                Row(
                    controls=[btn_refresh_list, model_upload_view],
                    alignment=MainAxisAlignment.START,
                    vertical_alignment=CrossAxisAlignment.START,
                ),
                # btn_refresh_list,
                # model_upload_view,
            ],
            spacing=30,
            scroll=True,
        )


if __name__ == "__main__":
    import flet as ft

    def dammy_func():
        pass

    def main(page: Page):
        page.add(
            UnityView(
                page,
                [
                    ModelView("Model A", dammy_func, dammy_func, dammy_func),
                    ModelView("Model B", dammy_func, dammy_func, dammy_func),
                    ModelView("Model C", dammy_func, dammy_func, dammy_func),
                ],
                dammy_func,
                dammy_func,
                dammy_func,
                dammy_func,
                dammy_func,
                dammy_func,
            )
        )

    ft.app(target=main)
