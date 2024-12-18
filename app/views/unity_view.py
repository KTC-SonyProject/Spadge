import logging

from flet import (
    Column,
    Container,
    ElevatedButton,
    FilePicker,
    Page,
    Row,
    Tab,
    TabAlignment,
    Tabs,
    Text,
    alignment,
)

from app.controller.file_controller import FileController
from app.views.core import BaseTabBodyView

logger = logging.getLogger(__name__)


class DisplaySettingsView(BaseTabBodyView):
    def __init__(self, page: Page):
        super().__init__(
            page,
            "Display",
        )

    def create_body(self):
        return Column(
            controls=[
                Text("**********************"),
                Text("Display settings body", size=20),
                Text("**********************"),
            ]
        )


class FileSettingsView(BaseTabBodyView):
    def __init__(self, page: Page, file_controller: FileController):
        super().__init__(
            page,
            "File",
        )
        self.controller = file_controller


    def create_body(self):
        self.file_picker = FilePicker(on_result=self.on_file_selected, on_upload=self.on_upload)
        self.page.overlay.append(self.file_picker)
        self.selected_files = Text("No files selected")
        self.upload_button = ElevatedButton(
            text="ファイルをアップロード",
            visible=False,
            on_click=self.upload_files,
        )
        return Column(
            alignment=alignment.center,
            expand=True,
            controls=[
                ElevatedButton(
                    text="ファイルを選択",
                    on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["txt", "pdf", "obj", "ply"]),
                ),
                self.selected_files,
                self.upload_button,
            ]
       )

    def on_file_selected(self, e):
        print(f"ファイルが選択されました: {e.files}")
        file_list = self.controller.handle_file_selection(e.files)
        if file_list:
            self.selected_files.value = ", ".join(map(lambda f: f.name, file_list))
            self.upload_button.visible = True
        else:
            self.selected_files.value = "No files selected"
            self.upload_button.visible = False
        self.page.update()

    def upload_files(self, e):
        try:
            upload_list = self.controller.prepare_upload_files(self.page)
            logger.debug(f"アップロードリスト: {upload_list}")
            self.file_picker.upload(upload_list)
        except Exception as error:
            logger.error(f"ファイルのアップロード中にエラーが発生しました: {error}")
            self.selected_files.value = "Error uploading files"
            self.upload_button.visible = False
            self.page.update()

    def on_upload(self, e):
        if e.progress is None:
            logger.error(f"アップロード中にエラーが発生しました: {e.error}")
            self.selected_files.value = "Error uploading files"
            self.upload_button.visible = False
            self.page.update()
        if e.progress == 1.0:
            self._on_upload_complete(e)
        else:
            self._on_upload_progress(e)

    def _on_upload_progress(self, e):
        logger.debug(f"アップロード中: {e.progress}")

    def _on_upload_complete(self, e):
        logger.debug(f"一時アップロードが完了しました: {e.file_name}")
        success, result = self.controller.send_file_to_unity(e.file_name)
        if success:
            self.selected_files.value = "ファイルのアップロードが完了しました"
        else:
            logger.error(f"Unityへのファイル送信中にエラーが発生しました: {result}")
            self.selected_files.value = "Error uploading files"
        self.upload_button.visible = False
        self.page.update()

# class FileSettingsBody(Column):
#     def __init__(self, page: Page):
#         super().__init__()
#         self.page = page
#         self.spacing = 10
#         self.file_picker = FilePicker(on_result=self.on_file_result, on_upload=self.on_file_upload)
#         self.page.overlay.append(self.file_picker)
#         self.selected_files = Text("No files selected")

#         self.controls = [
#             Text("**********************"),
#             Text("File Settings Body"),
#             Text("**********************"),
#             ElevatedButton(
#                 text="ファイルを選択",
#                 on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["txt", "pdf", "obj", "ply"]),
#             ),
#             self.selected_files,
#             ElevatedButton(
#                 visible=False,
#                 text="ファイルをアップロード",
#                 on_click=self.upload_files,
#             ),
#         ]

#     def on_file_result(self, e):
#         logger.debug(f"ファイルが選択されました: {e.files}")
#         self.selected_files.value = ", ".join(map(lambda f: f.name, e.files)) if e.files else "No files selected"
#         self.controls[5].visible = True if e.files else False
#         self.page.update()

#     def upload_files(self, e):
#         logger.debug(f"ファイルをアップロードします: {self.file_picker.result.files}")
#         upload_list = []
#         try:
#             if self.file_picker.result is not None and self.file_picker.result.files is not None:
#                 for f in self.file_picker.result.files:
#                     upload_list.append(
#                         FilePickerUploadFile(
#                             f.name,
#                             upload_url=self.page.get_upload_url(f.name, 600),
#                         )
#                     )
#                 self.file_picker.upload(upload_list)
#                 # file_picker.upload() の処理の途中経過や完了は on_file_upload() で処理
#         except Exception as error:
#             logger.error(f"ファイルのアップロード中にエラーが発生しました: {error}")
#             self.selected_files.value = "Error uploading files"
#             self.controls[5].visible = False
#             self.page.update()

#     def on_file_upload(self, e):
#         if e.progress == 1.0:  # アップロードが完了した場合Unityにファイルを送信
#             try:
#                 logger.debug("ファイルの一時アップロードが完了しました")
#                 # Unityにファイルを送信する
#                 file_path = f"{os.environ['FLET_ASSETS_DIR']}/uploads/{e.file_name}"
#                 result = self.page.data["server"].send_file(file_path)
#                 os.remove(file_path)  # 一時ファイルを削除
#                 self.controls[5].visible = False
#                 self.page.update()
#                 logger.debug(f"ファイルのアップロードが完了しました\nunity message: {result}")
#                 self.selected_files.value = "ファイルのアップロードが完了しました"
#                 self.page.update()
#             except ConnectionError as error:
#                 logger.error(f"Unityとの接続中にエラーが発生しました: {error}")
#                 os.remove(file_path)  # 一時ファイルを削除
#                 self.selected_files.value = "送信先のUnityと接続できませんでした。"
#                 self.controls[5].visible = False
#                 self.page.update()
#             except Exception as error:
#                 logger.error(f"ファイルのアップロード中にエラーが発生しました: {error}")
#                 self.selected_files.value = "Error uploading files"
#                 self.controls[5].visible = False
#                 self.page.update()


class TabBody(Tab):
    def __init__(self, page: Page, title: str, file_controller: FileController | None = None):
        super().__init__()
        self.page = page
        self.text = title
        self.expand = True

        if title == "Display":
            self.content = DisplaySettingsView(self.page)
        elif title == "File":
            self.content = FileSettingsView(self.page, file_controller)
        else:
            self.content = BaseTabBodyView(self.page, title)


class UnityView(Column):
    def __init__(self, page: Page, file_controller: FileController):
        super().__init__()
        self.page = page
        self.spacing = 10
        self.expand = True
        self.controls = [
            Container(
                padding=10,
                alignment=alignment.center,
                content=Row(
                    spacing=20,
                    controls=[
                        Text("Unity Application", size=30),
                        # ElevatedButton("Save Settings", on_click=self.save_settings),
                    ],
                ),
            ),
            Tabs(
                expand=True,
                selected_index=0,
                animation_duration=300,
                tab_alignment=TabAlignment.CENTER,
                tabs=[
                    TabBody(page, "Display"),
                    TabBody(page, "File", file_controller),
                    TabBody(page, "Other"),
                ],
            ),
        ]
