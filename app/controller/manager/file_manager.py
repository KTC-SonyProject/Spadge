import logging
import os
import zipfile

from flet import FilePickerUploadFile, Page

from app.controller.manager.obj_manager import ObjectDatabaseManager, ObjectManager
from app.controller.manager.server_manager import ServerManager
from app.controller.manager.settings_manager import SettingsManager
from app.models.command_models import TransferCommand
from app.models.database_models import DatabaseHandler
from app.models.file_models import FileModel

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(
        self,
        page: Page,
        socket_server: ServerManager,
        obj_database_manager: ObjectDatabaseManager,
        obj_manager: ObjectManager,
    ):  # obj_managerを追加
        self.model = FileModel(page)
        self.server = socket_server
        self.obj_database_manager = obj_database_manager  # obj_managerを初期化
        self.obj_manager = obj_manager  # obj_managerを初期化

    def handle_file_selection(self, files: list[FilePickerUploadFile]) -> list[FilePickerUploadFile] | None:
        """ファイル選択時にモデルを更新"""
        if files:
            selected_files = self.model.set_selected_files(files)
            logger.debug(f"選択されたファイル: {selected_files}")
            return selected_files
        else:
            return None

    def prepare_upload_single_file(self, file_name: str) -> FilePickerUploadFile:
        """ファイルの一時アップロード用URLを生成"""
        try:
            upload_url = self.model.get_upload_url(file_name)
            logger.debug(f"アップロードURL: {upload_url}")
            return FilePickerUploadFile(file_name, upload_url)
        except Exception as e:
            logger.error(f"ファイル準備中にエラー: {e}")
            raise e

    def prepare_upload_files(self) -> list[FilePickerUploadFile]:
        """ファイルの一時アップロード用URLを生成"""
        upload_list = []
        try:
            for f in self.model.selected_files:
                logger.debug(f"ファイル準備中: {f.name}")
                upload_url = self.model.get_upload_url(f.name)
                logger.debug(f"アップロードURL: {upload_url}")
                upload_list.append(FilePickerUploadFile(f.name, upload_url))
            return upload_list
        except Exception as e:
            logger.error(f"ファイル準備中にエラー: {e}")
            raise e

    def _send_file(self, command: TransferCommand) -> dict:
        """ファイルをUnityアプリに送信"""
        result = self.server.send_file(command)
        os.remove(command.file_path)  # 一時ファイルを削除
        return result

    def send_file_to_unity(self, file_name: str) -> tuple[bool, dict]:
        """Unityアプリにファイルを送信"""
        command = TransferCommand(self.model.get_file_path(file_name))
        try:
            # ファイルの確認
            self._file_check(command.file_path)

            if self._is_zip_file(command.file_path):
                # zipファイルの場合は解凍
                extracted_files = self._unzip_file(command.file_path)
                # 送信前にファイル名を連番にリネーム
                folder_path = os.path.dirname(command.file_path)
                renamed_files = self.rename_files_in_folder(folder_path, extracted_files)
                for renamed_file in renamed_files:
                    file_path = os.path.join(folder_path, renamed_file)
                    command = TransferCommand(file_path)
                    self._send_file(command)
                result = {"status_message": "OK", "message": "zipファイル送信完了"}
            else:
                result = self._send_file(command)
            logger.debug(f"Unity送信結果: {result}")
            return True, result
        except Exception as e:
            logger.error(f"Unity送信エラー: {e}")
            return False, {"status_message": "ERROR", "error_message": f"Unity送信エラー: {e}"}

    def _file_check(self, file_path: str) -> bool:
        """ファイルが存在するか確認"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        return True

    def _is_zip_file(self, file_path: str) -> bool:
        """ファイルがzip形式か確認"""
        if file_path.endswith(".zip"):
            return True
        else:
            return False

    def _unzip_file(self, file_path: str) -> list[str]:
        """ZIPファイルを解凍"""
        upload_dir = f"{os.environ['FLET_APP_STORAGE_TEMP']}/uploads"
        try:
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                extracted_files = []

                for entry in zip_ref.namelist():
                    # ディレクトリはスキップ
                    if entry.endswith("/"):
                        logger.debug(f"ディレクトリをスキップ: {entry}")
                        continue

                    extracted_file_path = os.path.join(upload_dir, entry)

                    # 必要なディレクトリを作成
                    os.makedirs(os.path.dirname(extracted_file_path), exist_ok=True)

                    # ファイルを展開
                    with zip_ref.open(entry) as source, open(extracted_file_path, "wb") as target:
                        target.write(source.read())

                    extracted_files.append(entry)

                logger.debug(f"展開されたファイル: {extracted_files}")
                return extracted_files
        except Exception as e:
            logger.error(f"ZIPファイル解凍エラー: {e}")
            raise e

    def rename_files_in_folder(self, folder_path: str, files: list[str]) -> list[str]:
        """フォルダー内のファイルを連番にリネームし、新しいファイル名のリストを返す"""
        renamed_files = []
        try:
            last_id = self.obj_database_manager.get_last_id()
            last_id += 1

            for file in files:
                file_extension = os.path.splitext(file)[1]
                old_file_path = os.path.join(folder_path, file)
                new_file_path = os.path.join(folder_path, f"{last_id}{file_extension}")
                os.rename(old_file_path, new_file_path)
                renamed_files.append(f"{last_id}{file_extension}")
            logger.debug(f"フォルダー内のファイルを連番にリネームしました: {folder_path}")
        except Exception as e:
            logger.error(f"ファイルリネーム中にエラー: {e}")
            raise e
        return renamed_files


if __name__ == "__main__":
    from app.controller.manager.settings_manager import SettingsManager

    settings_manager = SettingsManager()
    db_handler = DatabaseHandler(settings_manager)
    server = ServerManager()
    obj_database_manager = ObjectDatabaseManager(db_handler)
    obj_manager = ObjectManager(obj_database_manager, server)
    file_controller = FileManager(Page(), ServerManager(), obj_database_manager)
    file_controller.handle_file_selection(["test1.txt", "test2.txt"])
    print(file_controller.model.selected_files)

    if not os.path.exists(f"{file_controller.model.upload_url}/test1.txt"):
        # テストファイルがない場合は作成
        with open(f"{file_controller.model.upload_url}/test1.txt", "w") as f:
            f.write("test1.txt")
    print(file_controller.model.get_file_path("test1.txt"))  # /tmp/uploads/test1.txt

    # フォルダー内のファイルを連番にリネーム
    file_controller.rename_files_in_folder(os.path.join(os.environ["FLET_APP_STORAGE_TEMP"], "uploads"))
