import json
import os

import bcrypt


class AuthManager:
    """
    認証情報を管理するクラス

    Attributes:
        CREDENTIALS_FILE (str): 認証情報を保存するJSONファイルのパス
        credentials (dict): 認証情報を格納する辞書

    Methods:
        save_credentials: 認証情報をJSONファイルに保存する関数
        check_credentials: ユーザーIDとパスワードが正しいかどうかをチェックする関数
        update_credentials: ユーザーIDとパスワードを更新する関数
    """

    STORAGE_FOLDER = os.environ["FLET_APP_STORAGE_DATA"]
    CREDENTIALS_FILE = f"{STORAGE_FOLDER}/credentials.json"

    def __init__(self):
        self.credentials = self._load_credentials()

    def _load_credentials(self):
        """
        認証情報をJSONファイルから読み込む関数
        初期値はユーザーID: admin, パスワード: admin
        """
        if not os.path.exists(self.CREDENTIALS_FILE):
            DEFAULT_ID = "admin"
            DEFAULT_PASSWORD = "admin"
            hashed = bcrypt.hashpw(DEFAULT_PASSWORD.encode(), bcrypt.gensalt()).decode()
            default_credentials = {"id": DEFAULT_ID, "password": hashed}
            with open(self.CREDENTIALS_FILE, "w", encoding="utf-8") as f:
                json.dump(default_credentials, f, ensure_ascii=False, indent=4)
            return default_credentials
        with open(self.CREDENTIALS_FILE, encoding="utf-8") as f:
            return json.load(f)

    def _save_credentials(self):
        """
        認証情報をJSONファイルに保存する関数
        """
        with open(self.CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.credentials, f, ensure_ascii=False, indent=4)

    def check_credentials(self, user_id, password):
        """
        ユーザーIDとパスワードが正しいかどうかをチェックする関数
        """
        stored_id = self.credentials.get("id")
        stored_hashed = self.credentials.get("password")
        if user_id != stored_id:
            return False
        return bcrypt.checkpw(password.encode(), stored_hashed.encode())

    def update_credentials(self, new_id, new_password):
        """
        ユーザーIDとパスワードを更新する関数
        """
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        self.credentials = {"id": new_id, "password": hashed_password}
        self._save_credentials()


if __name__ == "__main__":
    auth_manager = AuthManager()

    # ユーザーIDとパスワードをチェック
    auth_manager.update_credentials("admin", "admin")
    print(auth_manager.check_credentials("admin", "admin"))  # True
    print(auth_manager.check_credentials("admin", "password"))  # False

    # 認証情報を更新して保存
    auth_manager.update_credentials("admin", "password")
    print(auth_manager.check_credentials("admin", "password"))  # True
    print(auth_manager.check_credentials("admin", "admin"))  # False



