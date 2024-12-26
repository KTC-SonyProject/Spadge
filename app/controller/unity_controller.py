import logging

from flet import (
    ElevatedButton,
    FilePicker,
    Page,
    Text,
)

from app.controller.core import AbstractController
from app.controller.file_controller import FileController
from app.views.core import TabView
from app.views.unity_view import (
    BaseUnityTabView,
    UnityView,
    create_display_settings_body,
    create_file_settings_body,
)

logger = logging.getLogger(__name__)


class UnityController(AbstractController):
    def __init__(self, page: Page, file_controller: FileController):
        super().__init__(page)
        self.file_controller = file_controller

    def _on_file_selected(self, e):
        logger.debug(f"Selected files: {e.files}")
        file_list = self.file_controller.handle_file_selection(e.files)
        if file_list:
            self.selected_files.value = ", ".join(map(lambda f: f.name, file_list))
            self.upload_button.visible = True
        else:
            self.selected_files.value = "No files selected"
            self.upload_button.visible = False
        self.page.update()

    def _upload_files(self, _):
        try:
            upload_list = self.file_controller.prepare_upload_files()
            logger.debug(f"Upload list: {upload_list}")
            self.file_picker.upload(upload_list)
        except Exception as err:
            logger.error(f"Error uploading files: {err}")
            self.selected_files.value = "Error uploading files"
            self.upload_button.visible = False
            self.page.update()

    def _on_upload(self, e):
        # TODO: uploadボタンを押した際の挙動がうまく動かない、今後修正予定
        if e.progress is None:
            logger.error(f"Error uploading files: {e.error}")
            self.selected_files.value = "Error uploading files"
            self.upload_button.visible = False
            self.page.update()
        if e.progress == 1.0:
            self._on_upload_complete(e)
        else:
            self._on_upload_progress(e)

    def _on_upload_progress(self, e):
        logger.debug(f"Uploading: {e.progress}")

    def _on_upload_complete(self, e):
        logger.debug(f"Temporary upload complete: {e.file_name}")
        success, result = self.file_controller.send_file_to_unity(e.file_name)
        if success:
            self.selected_files.value = "File upload complete"
        else:
            logger.error(f"Error sending file to Unity: {result}")
            self.selected_files.value = "Error uploading files"
        self.upload_button.visible = False
        self.page.update()

    def _create_display_settings_tab(self):
        return BaseUnityTabView(
            "Display",
            [create_display_settings_body()],
        )

    def _create_file_settings_tab(self):
        self.file_picker = FilePicker(on_result=self._on_file_selected, on_upload=self._on_upload)
        self.page.overlay.append(self.file_picker)
        self.selected_files = Text("No files selected")
        self.upload_button = ElevatedButton("Upload", visible=False, on_click=self._upload_files)

        return BaseUnityTabView(
            "File",
            [
                create_file_settings_body(
                    self.file_picker,
                    self.selected_files,
                    self.upload_button,
                ),
            ],
        )

    def get_view(self) -> UnityView:
        tabs = [
            TabView("Display", self._create_display_settings_tab()),
            TabView("File", self._create_file_settings_tab()),
        ]
        return UnityView(tabs=tabs)


if __name__ == "__main__":
    import flet as ft

    from app.controller.socket_server import SocketServer

    def main(page):
        server = SocketServer()
        file_controller = FileController(page, server)
        unity_controller = UnityController(page, file_controller)
        page.add(unity_controller.get_view())

    ft.app(target=main)
