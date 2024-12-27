# logging_config.py
import logging.config
import os
from datetime import datetime
from zoneinfo import ZoneInfo


class JSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # 日本標準時に変換
        dt = datetime.fromtimestamp(record.created, ZoneInfo("Asia/Tokyo"))
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()


STRAGE_DIR = os.getenv("FLET_APP_STORAGE_DATA", "logs")

LOGGING_CONFIG_FULL = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": JSTFormatter,
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
        "app_file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "level": "INFO",
            "filename": f"{STRAGE_DIR}/app.log",
            "mode": "a",
            "encoding": "utf-8",
        },
        "full_file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "level": "INFO",
            "filename": f"{STRAGE_DIR}/full.log",
            "mode": "a",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "app": {"handlers": ["console", "app_file", "full_file"], "level": "DEBUG", "propagate": False},
        "__main__": {"handlers": ["console", "app_file", "full_file"], "level": "DEBUG", "propagate": False},
        "": {"handlers": ["console", "app_file", "full_file"], "level": "INFO", "propagate": True},
    },
}

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": JSTFormatter,
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "__main__": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
}


def setup_logging(is_save_file: bool = False) -> None:
    """
    ロギング設定を行う

    Args:
        is_save_file (bool, optional): ログをファイルとして残すかどうか. Defaults to False.
    """
    if is_save_file:
        logging.config.dictConfig(LOGGING_CONFIG_FULL)
        # もしapp.logが存在していたら削除
        if os.path.exists(f"{STRAGE_DIR}/app.log"):
            os.remove(f"{STRAGE_DIR}/app.log")
    else:
        logging.config.dictConfig(LOGGING_CONFIG)
