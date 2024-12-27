import inspect
import logging
import re
from dataclasses import is_dataclass

logger = logging.getLogger(__name__)


def to_snake_case(name: str) -> str:
    """
    クラス名をスネークケースに変換する。
    Args:
        name (str): クラス名。

    Returns:
        str: スネークケースの名前。
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def get_dataclass_mapping(module) -> dict[str, type]:
    """
    指定されたモジュールからすべてのデータクラスを取得し、
    AppSettingsのフィールド名に一致させるマッピングを作成する。

    Args:
        module: データクラスを含むモジュール。

    Returns:
        dict: AppSettingsのフィールド名に一致するデータクラスのマッピング。
    """
    dataclasses = {}
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if is_dataclass(obj):
            # スネークケースに変換して一致させる
            field_name = to_snake_case(name)
            dataclasses[field_name] = obj
    # logger.debug(f"Dataclass mapping: {dataclasses}")
    return dataclasses


def safe_dataclass_init(cls, data: dict) -> object:
    """
    データクラスのフィールドに一致するデータのみを渡して初期化する。
    ネストされたデータクラスも再帰的に処理する。

    Args:
        cls: データクラスの型。
        data: 初期化に使用する辞書データ。

    Returns:
        初期化されたデータクラスのインスタンス。
    """
    if not is_dataclass(cls):
        raise ValueError(f"{cls}はデータクラスではありません。")

    field_names = {f.name: f for f in cls.__dataclass_fields__.values()}
    filtered_data = {
        key: (
            safe_dataclass_init(field_names[key].type, value)
            if hasattr(field_names[key].type, "__dataclass_fields__") and isinstance(value, dict)
            else value
        )
        for key, value in data.items()
        if key in field_names
    }
    return cls(**filtered_data)


if __name__ == "__main__":
    import app.models.settings_models as models

    # モジュールからデータクラスのマッピングを取得する
    mapping = get_dataclass_mapping(models)
    print(mapping)
