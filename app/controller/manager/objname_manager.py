import logging

from app.models.database_models import DatabaseHandler

logger = logging.getLogger(__name__)

class ObjectManager:
    """
    オブジェクト関連のデータ操作を提供するViewModel。
    """

    def __init__(self, db_handler: DatabaseHandler):
        """
        :param db_handler: DatabaseHandlerのインスタンス
        """
        self.db_handler = db_handler

    def get_name_by_id(self, object_id: int) -> str:
        """
        指定されたIDのオブジェクト名を取得する。
        :param object_id: オブジェクトID
        :return: {"object_name": str}
        """
        query = "SELECT object_name FROM object WHERE object_id = %s;"
        results = self.db_handler.fetch_query(query, (object_id,))
        if not results:
            raise ValueError(f"Object with ID {object_id} not found.")
        return results[0][0]

    def get_last_id(self) -> int:
        """
        テーブルの最後のIDを取得する。
        :return: 最後のオブジェクトID
        """
        query = "SELECT object_id FROM object ORDER BY object_id DESC LIMIT 1;"
        results = self.db_handler.fetch_query(query)
        if results:
            return results[0][0]
        return -1  # オブジェクトがない場合

    def update_name(self, object_id: int, new_name: str):
        """
        指定されたIDのオブジェクト名を更新する。
        :param object_id: オブジェクトID
        :param new_name: 新しい名前
        """
        query = "UPDATE object SET object_name = %s WHERE object_id = %s;"
        self.db_handler.execute_query(query, (new_name, object_id))


if __name__ == "__main__":
    # 設定を読み込み、DatabaseHandlerを初期化
    from app.controller.manager.settings_manager import SettingsManager

    settings_manager = SettingsManager()
    db_handler = DatabaseHandler(settings_manager)
    manager = ObjectManager(db_handler)

    try:
        # 最後のIDを取得
        last_id = manager.get_last_id()
        print(f"Last Object ID: {last_id}")

        # IDから名前を取得
        if last_id != -1:
            name = manager.get_name_by_id(last_id)
            print(f"Object Name with ID {last_id}: {name}")

        # 名前を変更
        if last_id != -1:
            new_name = "Updated Object Name"
            manager.update_name(last_id, new_name)
            updated_name = manager.get_name_by_id(last_id)
            print(f"Updated Object Name with ID {last_id}: {updated_name}")

    finally:
        # データベース接続を閉じる
        db_handler.close_connection()
