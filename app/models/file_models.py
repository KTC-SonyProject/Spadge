import logging
import os

from flet import FilePickerUploadFile, Page

logger = logging.getLogger(__name__)


class FileModel:
    def __init__(self, page: Page):
        self.page = page
        self.selected_files = []

    def set_selected_files(self, files: list[FilePickerUploadFile]) -> list[FilePickerUploadFile]:
        self.selected_files = files
        return self.selected_files

    def get_file_path(self, file_name: str) -> str:
        for file in self.selected_files:
            if file.name == file_name:
                file_path = f"{os.environ['FLET_APP_STORAGE_TEMP']}/uploads/{file.name}"
                logger.debug(f"get_file_path for: {file_path}")
                return file_path

    def get_upload_url(self, file_name: str) -> str:
        for file in self.selected_files:
            if file.name == file_name:
                return self.page.get_upload_url(file.name, 600)


if __name__ == "__main__":
    file_model = FileModel()
    file_model.set_selected_files(["test1.txt", "test2.txt"])
    print(file_model.selected_files)

    if not os.path.exists(f"{file_model.upload_url}/test1.txt"):
        # テストファイルがない場合は作成
        with open(f"{file_model.upload_url}/test1.txt", "w") as f:
            f.write("test1.txt")
    print(file_model.get_file_path("test1.txt"))  # /tmp/uploads/test1.txt
    print(file_model.get_file_path("test2.txt"))  # /tmp/uploads/test2.txt
    print(file_model.get_file_path("test3.txt"))  # None
