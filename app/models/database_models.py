import logging
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path

from psycopg_pool import ConnectionPool

from app.controller.settings_manager import SettingsManager

logger = logging.getLogger(__name__)


class BaseDatabaseHandler(ABC):
    """
    データベース操作のベースクラス。
    個別のデータベースクラスはこれを継承して実装する。
    """

    @abstractmethod
    def connect(self):
        """データベースに接続するための初期化処理"""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: tuple | None = None):
        """データを挿入、更新、削除するクエリを実行"""
        pass

    @abstractmethod
    def fetch_query(self, query: str, params: tuple | None = None) -> list[tuple]:
        """データを取得するクエリを実行"""
        pass

    @abstractmethod
    def close_connection(self):
        """データベース接続を閉じる"""
        pass


class SQLiteDatabaseHandler(BaseDatabaseHandler):
    def __init__(self, database_path: str, init_sql_path: str | None = None):
        self.database_path = database_path
        self.init_sql_path = init_sql_path
        self.connection: sqlite3.Connection | None = None
        self.connect()

    def connect(self):
        """SQLiteデータベースに接続する"""
        if not Path(self.database_path).exists():
            self._create_database()
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        logger.info("SQLite connection initialized.")

    def _create_database(self):
        """SQLiteデータベースを作成し初期化する"""
        Path(self.database_path).touch()
        if self.init_sql_path:
            with sqlite3.connect(self.database_path) as connection:
                with open(self.init_sql_path) as f:
                    connection.executescript(f.read())
            logger.info("SQLite database created with initial schema.")

    def execute_query(self, query: str, params: tuple | None = None):
        """クエリを実行（データ挿入、更新、削除）"""
        query = query.replace("%s", "?")  # SQLite形式に変換
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, params or [])

    def fetch_query(self, query: str, params: tuple | None = None) -> list[tuple]:
        """クエリを実行して結果を取得"""
        query = query.replace("%s", "?")  # SQLite形式に変換
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, params or [])
            return cursor.fetchall()

    def close_connection(self):
        """SQLite接続を閉じる"""
        if self.connection:
            self.connection.close()
            logger.info("SQLite connection closed.")


class PostgreSQLDatabaseHandler(BaseDatabaseHandler):
    def __init__(self, conninfo: str):
        self.conninfo = conninfo
        self.pool: ConnectionPool | None = None
        self.connect()

    def connect(self):
        """PostgreSQLデータベースに接続する"""
        self.pool = ConnectionPool(conninfo=self.conninfo, max_size=20, open=True)
        logger.info("PostgreSQL connection pool initialized.")

    def execute_query(self, query: str, params: tuple | None = None):
        """クエリを実行（データ挿入、更新、削除）"""
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()

    def fetch_query(self, query: str, params: tuple | None = None) -> list[tuple]:
        """クエリを実行して結果を取得"""
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def close_connection(self):
        """PostgreSQL接続を閉じる"""
        if self.pool:
            self.pool.close()
            logger.info("PostgreSQL connection pool closed.")


class DatabaseHandler:
    def __init__(self, settings_manager: SettingsManager):
        use_postgres = settings_manager.get_setting("database_settings.use_postgres")

        if use_postgres:
            conninfo = (
                f"postgresql://{settings_manager.get_setting('database_settings.postgres_settings.user')}:"
                f"{settings_manager.get_setting('database_settings.postgres_settings.password')}@"
                f"{settings_manager.get_setting('database_settings.postgres_settings.host')}:"
                f"{settings_manager.get_setting('database_settings.postgres_settings.port')}/"
                f"{settings_manager.get_setting('database_settings.postgres_settings.database')}?sslmode=disable"
            )
            self.handler = PostgreSQLDatabaseHandler(conninfo)
        else:
            database_path = settings_manager.get_setting("database_settings.sqlite_settings.database")
            init_sql_path = "db/sqlite/init/1_init.sql"
            self.handler = SQLiteDatabaseHandler(database_path, init_sql_path)

    def execute_query(self, query: str, params: tuple | None = None) -> None:
        self.handler.execute_query(query, params)

    def fetch_query(self, query: str, params: tuple | None = None) -> list[tuple]:
        return self.handler.fetch_query(query, params)

    def close_connection(self):
        self.handler.close_connection()


if __name__ == "__main__":
    from app.controller.settings_manager import SettingsManager

    settings_manager = SettingsManager()
    db = DatabaseHandler(settings_manager)

    try:
        # db.execute_query("INSERT INTO documents (title, content) VALUES (%s, %s)", ("Test Title", "Test Content"))
        documents = db.fetch_query("SELECT * FROM documents")
        print(documents)
    finally:
        db.close_connection()
