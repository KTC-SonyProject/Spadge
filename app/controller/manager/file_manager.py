import logging
import os

from flet import FilePickerUploadFile, Page

from app.controller.manager.server_manager import ServerManager
from app.models.command_models import TransferCommand
from app.models.file_models import FileModel

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self, page: Page, socket_server: ServerManager):
        self.model = FileModel(page)
        self.server = socket_server

    def handle_file_selection(self, files: list[FilePickerUploadFile]) -> list[FilePickerUploadFile] | None:
        """ファイル選択時にモデルを更新"""
        if files:
            selected_files = self.model.set_selected_files(files)
            logger.debug(f"選択されたファイル: {selected_files}")
            return selected_files
        else:
            return None

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

    def send_file_to_unity(self, file_name: str) -> tuple[bool, dict]:
        """Unityアプリにファイルを送信"""
        command = TransferCommand(self.model.get_file_path(file_name))
        try:
            # ファイルの確認
            self._file_check(command.file_path)

            logger.debug(f"Unityにファイル送信中: {command.file_path}")
            result = self.server.send_file(command)
            os.remove(command.file_path)  # 一時ファイルを削除
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


if __name__ == "__main__":
    file_controller = FileManager(ServerManager())
    file_controller.handle_file_selection(["test1.txt", "test2.txt"])
    print(file_controller.model.selected_files)

    if not os.path.exists(f"{file_controller.model.upload_url}/test1.txt"):
        # テストファイルがない場合は作成
        with open(f"{file_controller.model.upload_url}/test1.txt", "w") as f:
            f.write("test1.txt")
    print(file_controller.model.get_file_path("test1.txt"))  # /tmp/uploads/test1.txt
