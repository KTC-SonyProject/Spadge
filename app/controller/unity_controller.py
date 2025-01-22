import logging

from flet import (
    ElevatedButton,
    FilePicker,
    Page,
    Text,
)

from app.controller.core import AbstractController
from app.controller.manager import (
    FileManager,
    ServerManager,
)
from app.models.command_models import ListCommand
from app.views.core import TabView
from app.views.unity_view import (
    BaseUnityTabView,
    UnityView,
    create_display_settings_body,
    create_file_settings_body,
    ObjListView,
)

logger = logging.getLogger(__name__)


class UnityController(AbstractController):
    def __init__(self, page: Page, file_manager: FileManager, socket_server: ServerManager):
        super().__init__(page)
        self.file_manager = file_manager
        self.server = socket_server

    def _get_list(self):
        command = ListCommand()
        res_json = self.server.send_command(command)
        logger.debug(f"Response: {res_json}")
        # jsonの中からresultの値を取得
        # resultがない場合は空のリストを返す
        try:
            obj_list = res_json["result"]
        except KeyError:
            obj_list = None
        logger.debug(f"Object list: {obj_list}")
        return obj_list

    def _on_file_selected(self, e):
        logger.debug(f"Selected files: {e.files}")
        file_list = self.file_manager.handle_file_selection(e.files)
        if file_list:
            self.selected_files.value = ", ".join(map(lambda f: f.name, file_list))
            self.upload_button.visible = True
        else:
            self.selected_files.value = "No files selected"
            self.upload_button.visible = False
        self.page.update()

    def _upload_file(self, file_name):
        logger.debug(f"Uploading: {file_name}")
        upload_file = self.file_manager.prepare_upload_single_file(file_name)
        self.file_picker.upload([upload_file])

    def _upload_files(self, _):
        try:
            for f in self.file_manager.model.selected_files:
                self._upload_file(f.name)
        except Exception as err:
            logger.error(f"Error uploading files: {err}")
            self.selected_files.value = "Error uploading files"
            self.upload_button.visible = False
            self.page.update()

    def _on_upload(self, e):
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
        success, result = self.file_manager.send_file_to_unity(e.file_name)
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
            [ObjListView(self._get_list)],
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

    from app.controller.manager.server_manager import ServerManager

    def main(page):
        server = ServerManager()
        file_manager = FileManager(page, server)
        unity_controller = UnityController(page, file_manager)
        page.add(unity_controller.get_view())

    ft.app(target=main)
