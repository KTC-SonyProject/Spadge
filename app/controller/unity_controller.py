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
    ObjectDatabaseManager,
    ServerManager,
    SettingsManager,
)
from app.models.database_models import DatabaseHandler
from app.views.core import TabView
from app.views.unity_view import (
    BaseUnityTabView,
    ObjListView,
    UnityView,
    create_file_settings_body,
)

logger = logging.getLogger(__name__)


class UnityController(AbstractController):
    def __init__(
        self, page: Page, file_manager: FileManager, socket_server: ServerManager, obj_database_manager: ObjectDatabaseManager
    ):
        super().__init__(page)
        self.file_manager = file_manager
        self.server = socket_server
        self.obj_database_manager = obj_database_manager

    # リストを取得
    def _get_list(self):
        try:
            objects = self.obj_database_manager.get_all_objects()  # ObjectManagerのget_all_objectsを利用
            obj_list = [obj["object_name"] for obj in objects]  # オブジェクト名のリストを生成
        except KeyError:
            obj_list = []
        logger.debug(f"Object list: {obj_list}")
        return obj_list

    # ファイル選択時の処理
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

    # ファイルアップロード
    def _upload_file(self, file_name):
        logger.debug(f"Uploading: {file_name}")
        upload_file = self.file_manager.prepare_upload_single_file(file_name)
        self.file_picker.upload([upload_file])

    # ファイルアップロード(複数)
    def _upload_files(self, _):
        try:
            for f in self.file_manager.model.selected_files:
                self._upload_file(f.name)
        except Exception as err:
            logger.error(f"Error uploading files: {err}")
            self.selected_files.value = "Error uploading files"
            self.upload_button.visible = False
            self.page.update()

    # アップロード処理
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

    # アップロード進捗
    def _on_upload_progress(self, e):
        logger.debug(f"Uploading: {e.progress}")

    # アップロード完了
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

    # タブ作成
    def _create_display_settings_tab(self):
        return BaseUnityTabView(
            "Display",
            [ObjListView(self._get_list)],
        )

    # ファイルタブ作成
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

    # ビュー取得
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
        settings = SettingsManager()
        db_handler = DatabaseHandler(settings)
        obj_database_manager = ObjectDatabaseManager(db_handler)
        file_manager = FileManager(page, server, obj_database_manager)
        unity_controller = UnityController(page, file_manager, server, obj_database_manager)
        page.add(unity_controller.get_view())

    ft.app(target=main)
