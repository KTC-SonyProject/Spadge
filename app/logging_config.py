# logging_config.py
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "level": "INFO",
            "filename": "app.log",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": True},
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
