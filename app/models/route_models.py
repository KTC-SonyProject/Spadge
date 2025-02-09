from dataclasses import dataclass
from enum import Enum

from flet import (
    View,
)


class RouteParamKey(Enum):
    SETTINGS = "settings_manager"
    DB_HANDLER = "db_handler"
    DOCS_MANAGER = "docs_manager"
    SERVER = "socket_server"
    SERVER_THREAD = "server_thread"
    FILE_MANAGER = "file_manager"
    AUTH_MANAGER = "auth_manager"
    OBJ_MANAGER = "obj_manager"


class RouteParamValue(Enum):
    SETTINGS = "data:settings_manager"
    DB_HANDLER = "data:db_handler"
    DOCS_MANAGER = "data:docs_manager"
    SERVER = "data:socket_server"
    SERVER_THREAD = "data:server_thread"
    FILE_MANAGER = "data:file_manager"
    AUTH_MANAGER = "data:auth_manager"
    OBJ_MANAGER = "data:obj_manager"


@dataclass
class RouteParam:
    key: RouteParamKey | str
    value: RouteParamValue | str | int


@dataclass
class RouteItem:
    title: str
    layout: View
    params: list[RouteParam] | None = None
