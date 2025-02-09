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
        query = "SELECT object_name FROM objects WHERE object_id = %s;"
        results = self.db_handler.fetch_query(query, (object_id,))
        if not results:
            raise ValueError(f"Objects with ID {object_id} not found.")
        return results[0][0]

    def get_all_objects(self) -> list[dict]:
        """
        全てのオブジェクトを取得する。
        :return: {"object_id": int, "object_name": str}のリスト
        """
        query = "SELECT object_id, object_name FROM objects;"
        results = self.db_handler.fetch_query(query)
        return [{"object_id": row[0], "object_name": row[1]} for row in results] if results else []

    def get_last_id(self) -> int:
        """
        テーブルの最後のIDを取得する。
        :return: 最後のオブジェクトID（オブジェクトがない場合は0）
        """
        query = "SELECT object_id FROM objects ORDER BY object_id DESC LIMIT 1;"
        results = self.db_handler.fetch_query(query)
        if results:
            return results[0][0]
        return 0  # オブジェクトがない場合は0から開始

    def new_object(self, object_name: str) -> int:
        """
        新しいオブジェクトを追加する。
        :param object_name: オブジェクト名
        :return: 追加されたオブジェクトのID
        """
        query = "INSERT INTO objects (object_name) VALUES (%s) RETURNING object_id;"
        results = self.db_handler.fetch_query(query, (object_name,))
        if results:
            return results[0][0]
        else:
            raise RuntimeError("Failed to insert new object.")


    def update_name(self, object_id: int, new_name: str):
        """
        指定されたIDのオブジェクト名を更新する。
        :param object_id: オブジェクトID
        :param new_name: 新しい名前
        """
        query = "UPDATE objects SET object_name = %s WHERE object_id = %s;"
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

        # 全てのオブジェクトを取得
        all_objects = manager.get_all_objects()
        print("All Objects:")

        # 名前を変更
        if last_id != -1:
            new_name = "Updated Objects Name"
            manager.update_name(last_id, new_name)
            updated_name = manager.get_name_by_id(last_id)
            print(f"Updated Object Name with ID {last_id}: {updated_name}")

    finally:
        # データベース接続を閉じる
        db_handler.close_connection()
