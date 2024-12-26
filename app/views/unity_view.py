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
            ElevatedButton(
                text="ファイルを選択",
                on_click=lambda _: file_picker.pick_files(allowed_extensions=["txt", "pdf", "obj", "ply"]),
            ),
            selected_files,
            upload_button,
        ],
    )


# class FileSettingsView(BaseTabBodyView):
#     def __init__(self, page: Page, file_controller: FileController):
#         super().__init__(
#             page,
#             "File",
#         )
#         self.controller = file_controller

#     def create_body(self):
#         self.file_picker = FilePicker(on_result=self.on_file_selected, on_upload=self.on_upload)
#         self.page.overlay.append(self.file_picker)
#         self.selected_files = Text("No files selected")
#         self.upload_button = ElevatedButton(
#             text="ファイルをアップロード",
#             visible=False,
#             on_click=self.upload_files,
#         )
#         return Column(
#             alignment=alignment.center,
#             expand=True,
#             controls=[
#                 ElevatedButton(
#                     text="ファイルを選択",
#                     on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["txt", "pdf", "obj", "ply"]),
#                 ),
#                 self.selected_files,
#                 self.upload_button,
#             ],
#         )

#     def on_file_selected(self, e):
#         print(f"ファイルが選択されました: {e.files}")
#         file_list = self.controller.handle_file_selection(e.files)
#         if file_list:
#             self.selected_files.value = ", ".join(map(lambda f: f.name, file_list))
#             self.upload_button.visible = True
#         else:
#             self.selected_files.value = "No files selected"
#             self.upload_button.visible = False
#         self.page.update()

#     def upload_files(self, e):
#         try:
#             upload_list = self.controller.prepare_upload_files(self.page)
#             logger.debug(f"アップロードリスト: {upload_list}")
#             self.file_picker.upload(upload_list)
#         except Exception as error:
#             logger.error(f"ファイルのアップロード中にエラーが発生しました: {error}")
#             self.selected_files.value = "Error uploading files"
#             self.upload_button.visible = False
#             self.page.update()

#     def on_upload(self, e):
#         if e.progress is None:
#             logger.error(f"アップロード中にエラーが発生しました: {e.error}")
#             self.selected_files.value = "Error uploading files"
#             self.upload_button.visible = False
#             self.page.update()
#         if e.progress == 1.0:
#             self._on_upload_complete(e)
#         else:
#             self._on_upload_progress(e)

#     def _on_upload_progress(self, e):
#         logger.debug(f"アップロード中: {e.progress}")

#     def _on_upload_complete(self, e):
#         logger.debug(f"一時アップロードが完了しました: {e.file_name}")
#         success, result = self.controller.send_file_to_unity(e.file_name)
#         if success:
#             self.selected_files.value = "ファイルのアップロードが完了しました"
#         else:
#             logger.error(f"Unityへのファイル送信中にエラーが発生しました: {result}")
#             self.selected_files.value = "Error uploading files"
#         self.upload_button.visible = False
#         self.page.update()


# class TabBody(Tab):
#     def __init__(self, page: Page, title: str, file_controller: FileController | None = None):
#         super().__init__()
#         self.page = page
#         self.text = title
#         self.expand = True

#         if title == "Display":
#             self.content = DisplaySettingsView(self.page)
#         elif title == "File":
#             self.content = FileSettingsView(self.page, file_controller)
#         else:
#             self.content = BaseTabBodyView(self.page, title)


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
