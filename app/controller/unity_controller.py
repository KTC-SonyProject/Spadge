import logging

from flet import (
    Colors,
    ElevatedButton,
    FilePicker,
    Page,
    Text,
    TextField,
)

from app.controller.core import AbstractController
from app.controller.manager import (
    AuthManager,
    FileManager,
    ObjectDatabaseManager,
    ObjectManager,
    ServerManager,
    SettingsManager,
)
from app.models.database_models import DatabaseHandler
from app.views.core import TabView
from app.views.unity_view import (
    BaseUnityTabView,
    ModelUploadView,
    ModelView,
    ObjListView,
    OldUnityView,
    UnityView,
    create_file_settings_body,
    create_update_model_modal,
)

logger = logging.getLogger(__name__)


class OldUnityController(AbstractController):
    def __init__(
        self,
        page: Page,
        file_manager: FileManager,
        socket_server: ServerManager,
        obj_database_manager: ObjectDatabaseManager,
        obj_manager: ObjectManager,
    ):
        super().__init__(page)
        self.file_manager = file_manager
        self.server = socket_server
        self.obj_database_manager = obj_database_manager
        self.obj_manager = obj_manager

    # リストを取得
    def _get_list(self):
        try:
            objects = self.obj_database_manager.get_all_objects()  # ObjectDatabaseManagerのget_all_objectsを利用
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
            [ObjListView(self._get_list, self._change_obj_by_id)],
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

    def _change_obj_by_id(self, obj):
        self.obj_manager.change_obj_by_id(obj)

    # ビュー取得
    def get_view(self) -> UnityView:
        tabs = [
            TabView("Display", self._create_display_settings_tab()),
            TabView("File", self._create_file_settings_tab()),
        ]
        return OldUnityView(tabs=tabs)


# ------------------------新旧の境目------------------------

class UnityController(AbstractController):
    def __init__(
        self,
        page: Page,
        file_manager: FileManager,
        socket_server: ServerManager,
        obj_database_manager: ObjectDatabaseManager,
        obj_manager: ObjectManager,
        auth_manager: AuthManager,
    ):
        super().__init__(page)
        self.file_manager = file_manager
        self.server = socket_server
        self.obj_database_manager = obj_database_manager
        self.obj_manager = obj_manager
        self.auth_manager = auth_manager
        self._initialize_model_upload_view()

    def _initialize_model_upload_view(self):
        self.file_picker = FilePicker(on_result=self.on_file_selected, on_upload=self.on_upload)
        self.page.overlay.append(self.file_picker)
        self.model_upload_view = ModelUploadView(
            upload_model=self.upload_files,
            file_picker=self.file_picker,
            is_authenticated=self.auth_manager.check_is_authenticated(),
        )

    def _create_add_modal(self, model_id):
        """モーダルを作成する処理"""
        def no_func(_):
            self.add_model_modal.open = False
            self.page.update()

        def yes_func(_):
            # TODO: モデル名の更新処理をテストするためにコメントアウト中
            # self.obj_database_manager.update_name(model_id, self.add_model_modal.content.value)
            logger.debug(f"Update model name: {model_id} -> {self.add_model_modal.content.value}")
            self.add_model_modal.open = False
            self.page.update()

        self.add_model_modal = create_update_model_modal(
            content=TextField(
                label="モデル名",
                hint_text="モデル名を入力",
                filled=True,
            ),
            yes_func=yes_func,
            no_func=no_func,
        )
        return self.add_model_modal

    def open_modal(self, model_id):
        """モーダルを開く処理"""
        self.page.overlay.append(self._create_add_modal(model_id))
        self.add_model_modal.open = True
        self.page.update()

    def on_file_selected(self, e):
        """ファイルを選択したときの処理"""
        logger.debug(f"Selected files: {e.files}")
        file_list = self.file_manager.handle_file_selection(e.files)
        if file_list:
            self.model_upload_view.add_model_file_name.value = ", ".join(map(lambda f: f.name, file_list))
            self.model_upload_view.btn_upload_model.visible = True
            self.model_upload_view.add_model_name.visible = True
        else:
            self.model_upload_view.add_model_file_name.value = "ファイルが選択されていません"
            self.model_upload_view.btn_upload_model.visible = False
            self.model_upload_view.add_model_name.visible = False
        self.page.update()

    def _upload_file(self, file_name):
        """ファイルをアップロードするときの処理"""
        logger.debug(f"Uploading: {file_name}")
        upload_file = self.file_manager.prepare_upload_single_file(file_name)
        self.file_picker.upload([upload_file])

    def upload_files(self, _):
        """複数のファイルアップロード処理"""
        try:
            for f in self.file_manager.model.selected_files:
                self._upload_file(f.name)
        except Exception as err:
            logger.error(f"Error uploading files: {err}")
            self.model_upload_view.add_model_file_name.value = "モデルのアップロードに失敗しました"
            self.upload_button.visible = False
            self.page.update()

    def on_upload(self, e):
        """アップロード処理"""
        if e.progress is None:
            logger.error(f"Error uploading files: {e.error}")
            self.model_upload_view.add_model_file_name.value = "モデルのアップロードに失敗しました"
            self.model_upload_view.visible = False
            self.page.update()
        elif e.progress == 1.0:
            self._on_upload_complete(e)
        else:
            self._on_upload_progress(e)

    def _on_upload_progress(self, e):
        """アップロード進捗"""
        logger.debug(f"Uploading: {e.progress}")

    def _on_upload_complete(self, e):
        """アップロード完了"""
        logger.debug(f"Temporary upload complete: {e.file_name}")
        # TODO: モデルの名前をアップロード時に選択できるようにしたので、それに対応させる
        # self.model_upload_view.add_model_name.valueで入力された名前を取得できる
        success, result = self.file_manager.send_file_to_unity(e.file_name)
        if success:
            self.model_upload_view.add_model_file_name.value = "モデルのアップロードが完了しました"
        else:
            logger.error(f"Error sending file to Unity: {result}")
            self.model_upload_view.add_model_file_name.value = "モデルのアップロードに失敗しました"
        self.model_upload_view.btn_upload_model.visible = False
        self.page.update()

    def _get_list(self):
        try:
            objects = self.obj_database_manager.get_all_objects()  # ObjectDatabaseManagerのget_all_objectsを利用
        except KeyError:
            objects = []
        logger.debug(f"Object list: {objects}")
        return objects

    def _get_model_view_list(self):
        """モデルビューのリストを取得"""
        objects = self._get_list()
        if objects:
            model_list = [
                ModelView(
                    model_name=obj["object_name"],
                    show_obj=lambda id=obj["object_id"]: self.obj_manager.change_obj_by_id(id),
                    update_obj_name=lambda _, id=obj["object_id"]: self.open_modal(id),
                    delete_obj=lambda _, id=obj["object_id"]: print(f"Delete object: {id}"),  # TODO: modelの削除処理を追加
                    is_authenticated=self.auth_manager.check_is_authenticated(),
                )
                for obj in objects
            ]
            return model_list
        else:
            return [Text("まだオブジェクトが登録されていません", size=20, color=Colors.YELLOW_700)]

    def refresh_list(self):
        self.view.model_list = self._get_model_view_list()
        self.page.update()

    def get_unity_status(self):
        if self.server.is_connected:
            return Text("ディスプレイアプリ 接続状況: ✅ 接続中", size=16, color=Colors.GREEN_700)
        else:
            return Text("ディスプレイアプリ 接続状況: ❌ 未接続", size=16, color=Colors.RED_700)

    def refresh_unity_status(self):
        self.view.unity_status = self.get_unity_status()
        self.page.update()

    def _get_current_obj_name(self) -> str:
        """現在のオブジェクト名を取得"""
        if self.server.is_connected:
            # TODO: 現在のオブジェクト名を取得する処理を追加
            obj = "Nao"
            return obj
        else:
            return "不明"

    def get_view(self) -> UnityView:
        self.model_list = self._get_model_view_list()
        self.view = UnityView(
            page=self.page,
            model_list=self.model_list,
            model_upload_view=self.model_upload_view,
            refresh_list=self.refresh_list,
            unity_status=self.get_unity_status(),
            refresh_status=self.refresh_unity_status,
            show_current_obj_name=self._get_current_obj_name(),
            rotate_start=lambda: print("Rotate start"),  # TODO: rotate_startの処理を追加
            rotate_stop=lambda: print("Rotate stop"),  # TODO: rotate_stopの処理を追加
        )
        return self.view


if __name__ == "__main__":
    import flet as ft

    from app.controller.manager.server_manager import ServerManager

    def main(page):
        server = ServerManager()
        settings = SettingsManager()
        db_handler = DatabaseHandler(settings)
        obj_database_manager = ObjectDatabaseManager(db_handler)
        obj_manager = ObjectManager(obj_database_manager, server)
        file_manager = FileManager(page, server, obj_database_manager, obj_manager)
        unity_controller = UnityController(page, file_manager, server, obj_database_manager)
        page.add(unity_controller.get_view())

    ft.app(target=main)
