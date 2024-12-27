import logging

from app.models.database_models import DatabaseHandler

logger = logging.getLogger(__name__)


class DocumentsManager:
    """
    ドキュメント関連のデータ操作を提供するViewModel。
    """

    def __init__(self, db_handler: DatabaseHandler):
        """
        :param db_handler: DatabaseHandlerのインスタンス
        """
        self.db_handler = db_handler

    def get_all_documents(self) -> list[dict[str, str]]:
        """
        全てのドキュメントを取得する。
        :return: ドキュメントリスト [{"id": int, "title": str}, ...]
        """
        query = "SELECT document_id, title FROM documents ORDER BY document_id ASC;"
        results = self.db_handler.fetch_query(query)
        return [{"id": row[0], "title": row[1]} for row in results]

    def get_document_by_id(self, document_id: int) -> dict[str, str]:
        """
        指定されたIDのドキュメントを取得する。
        :param document_id: ドキュメントID
        :return: {"id": int, "title": str, "content": str}
        """
        query = "SELECT document_id, title, content FROM documents WHERE document_id = %s;"
        results = self.db_handler.fetch_query(query, (document_id,))
        if not results:
            raise ValueError(f"Document with ID {document_id} not found.")
        result = results[0]
        return {"id": result[0], "title": result[1], "content": result[2]}

    def add_document(self, title: str, content: str = "") -> int:
        """
        新しいドキュメントを追加する。
        :param title: ドキュメントのタイトル
        :param content: ドキュメントの内容
        :return: 新しいドキュメントのID
        """
        query = "INSERT INTO documents (title, content) VALUES (%s, %s) RETURNING document_id;"
        results = self.db_handler.fetch_query(query, (title, content))
        return results[0][0] if results else -1

    def update_document(self, document_id: int, title: str, content: str):
        """
        指定されたドキュメントを更新する。
        :param document_id: ドキュメントID
        :param title: 新しいタイトル
        :param content: 新しい内容
        """
        query = "UPDATE documents SET title = %s, content = %s WHERE document_id = %s;"
        self.db_handler.execute_query(query, (title, content, document_id))

    def delete_document(self, document_id: int):
        """
        指定されたIDのドキュメントを削除する。
        :param document_id: ドキュメントID
        """
        query = "DELETE FROM documents WHERE document_id = %s;"
        self.db_handler.execute_query(query, (document_id,))


if __name__ == "__main__":
    # 設定を読み込み、DatabaseHandlerを初期化
    from app.controller.manager.settings_manager import SettingsManager

    settings_manager = SettingsManager()
    db_handler = DatabaseHandler(settings_manager)
    manager = DocumentsManager(db_handler)

    try:
        # 全てのドキュメントを取得
        documents = manager.get_all_documents()
        print("All Documents:", documents)

        # 新しいドキュメントを追加
        new_document_id = manager.add_document("Sample Title", "Sample Content")
        print(f"New Document ID: {new_document_id}")

        # 新しく追加したドキュメントを取得
        new_document = manager.get_document_by_id(new_document_id)
        print("New Document:", new_document)

        # ドキュメントを更新
        manager.update_document(new_document_id, "Updated Title", "Updated Content")
        updated_document = manager.get_document_by_id(new_document_id)
        print("Updated Document:", updated_document)

        # ドキュメントを削除
        manager.delete_document(new_document_id)
        print(f"Document with ID {new_document_id} deleted.")

    finally:
        # データベース接続を閉じる
        db_handler.close_connection()
