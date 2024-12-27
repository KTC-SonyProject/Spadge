import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.controller.utils import get_dataclass_mapping, safe_dataclass_init
from app.models import settings_models as models
from app.models.settings_models import (
    DEFAULT_SETTINGS,
    AppSettings,
)

# ロギング設定
logger = logging.getLogger(__name__)


class SettingsManager:
    """
    設定のロード、操作、保存を行うManagerクラス。
    """

    # STORAGE_FOLDER = os.environ["FLET_APP_STORAGE_DATA"]
    SETTINGS_FILE = "local.settings.json"

    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self) -> Any:
        """
        設定をファイルからロードする。
        ファイルが存在しない場合はデフォルト設定を使用する。
        """
        if Path(self.SETTINGS_FILE).exists():
            try:
                with open(self.SETTINGS_FILE, encoding="utf-8") as file:
                    data = json.load(file)
                    logger.debug(f"ロードした設定: {data}")
                logger.info("設定ファイルを正常にロードしました。")
                return self._dict_to_app_settings(data)
            except (json.JSONDecodeError, KeyError):
                logger.error("設定ファイルの読み込み中にエラーが発生しました。デフォルト設定を使用します。")
        else:
            logger.warning("設定ファイルが存在しません。デフォルト設定を使用します。")
            return DEFAULT_SETTINGS

    def save_settings(self):
        """
        現在の設定をファイルに保存する。
        """
        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(asdict(self.settings), file, indent=4, ensure_ascii=False)
        logger.info("設定を保存しました。")

    def get_setting(self, path: str) -> Any:
        """
        指定されたパスの設定値を取得する。
        例: "general_settings.app_name"
        """
        try:
            keys = path.split(".")
            value = self.settings
            for key in keys:
                value = getattr(value, key, None)
                if value is None:
                    raise AttributeError(f"キーが見つかりません: {path}")
            logger.debug(f"取得した設定: {path} = {value}")
            return value
        except AttributeError as e:
            logger.error(f"設定の取得中にエラーが発生しました: {e}")
            return None

    def update_setting(self, path: str, value: Any):
        """
        指定されたパスの設定値を更新する。
        例: "general_settings.app_name", "New App"
        """
        try:
            keys = path.split(".")
            target = self.settings
            for key in keys[:-1]:
                target = getattr(target, key, None)
                if target is None:
                    raise KeyError(f"設定項目が見つかりません: {path}")
            if hasattr(target, keys[-1]):
                setattr(target, keys[-1], value)
                logger.debug(f"設定を更新しました: {path} = {value}")
            else:
                raise KeyError(f"設定項目が見つかりません: {path}")
        except KeyError as e:
            logger.error(f"設定の更新中にエラーが発生しました: {e}")

    def _dict_to_app_settings(self, data: dict) -> Any:
        """
        辞書からAppSettingsオブジェクトを生成する。
        データクラスを動的に処理する。
        """
        try:
            # AppSettingsフィールド名と対応するマッピング作成
            section_classes = get_dataclass_mapping(models)
            section_data = {}

            for field_name, cls in section_classes.items():
                if field_name in data:
                    raw_data = data[field_name]
                    section_data[field_name] = safe_dataclass_init(cls, raw_data)

            return AppSettings(**section_data)

        except TypeError as e:
            logger.error(f"設定オブジェクトの生成中にエラーが発生しました: {e}")
            return DEFAULT_SETTINGS


def load_settings(key) -> dict:
    """
    指定されたキーの設定をファイルからロードして辞書型で返す。
    値を取得するのみ使用でき、設定の更新はできない。
    """
    try:
        with open("local.settings.json", encoding="utf-8") as file:
            data = json.load(file)
            return data[key]
    except (json.JSONDecodeError, KeyError):
        logger.error("設定ファイルの読み込み中にエラーが発生しました。")
        return {}


if __name__ == "__main__":
    from app.logging_config import setup_logging

    setup_logging()
    manager = SettingsManager()
    print("現在の設定:", manager.settings)

    # 設定の取得例
    app_name = manager.get_setting("general_settings.app_name")
    print("アプリ名:", app_name)

    # 設定の更新例
    manager.update_setting("general_settings.app_name", "New App")
    manager.update_setting("database_settings.use_postgres", True)
    manager.update_setting("database_settings.postgres_settings.host", "localhost")
    manager.save_settings()

    print("更新後の設定:", manager.settings)

    print(load_settings("general_settings"))
