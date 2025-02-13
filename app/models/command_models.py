import json
import logging
import os

logger = logging.getLogger(__name__)


class CommandBase:
    """
    コマンドの基底クラス
    """

    def __init__(self, command_name: str | None = None, body_size: int | None = None, command_body: dict | None = None):
        self._command_name = command_name
        self._body_size = body_size
        self._command_body = command_body

    def __str__(self):
        try:
            return (
                f"command_name: {self.command_name}, \nbody_size: {self.body_size}, \ncommand_body: {self.command_body}"
            )
        except ValueError as e:
            logger.warning(f"コマンドが不正です: {e}")
            return (
                f"command_name: {self._command_name}, \n"
                f"body_size: {self._body_size}, \n"
                f"command_body: {self._command_body}"
            )

    def get_command(self):
        self.convert_body()
        return f"{self.command_header}\n{self.get_body_to_str()}"

    @property
    def command_name(self) -> str:
        if self._command_name is None:
            raise ValueError("command_nameが設定されていません")
        return self._command_name

    @command_name.setter
    def command_name(self, value: str):
        if not isinstance(value, str):
            raise ValueError("command_nameは文字列で指定してください")
        self._command_name = value

    @property
    def body_size(self) -> int:
        if self._body_size is None:
            raise ValueError("body_sizeが設定されていません。command_bodyを設定してください")
        return self._body_size

    @property
    def command_body(self) -> dict:
        if self._command_body is None:
            raise ValueError("command_bodyが設定されていません")
        return self._command_body

    @command_body.setter
    def command_body(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("command_bodyは辞書型で指定してください")
        self._body_size = len(str(value).encode("utf-8"))
        self._command_body = value

    def get_body_to_str(self) -> str:
        """
        コマンドのボディを文字列に変換

        Returns:
            str: コマンドのボディ
        """
        return json.dumps(self.command_body)

    @property
    def command_header(self) -> str:
        """
        コマンドのヘッダーを生成する

        Returns:
            str: コマンドのヘッダー
        """
        return f"{self.command_name} {self.body_size}"

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        raise NotImplementedError("convert_bodyメソッドが実装されていません")


class ControlCommand(CommandBase):
    """
    制御コマンドを管理するクラス
    """

    def __init__(self, object_id: str | None = None, action: str | None = None, action_parameters: dict | None = None):
        super().__init__(
            command_name="CONTROL",
        )
        self._object_id = object_id
        self._action = action
        self._action_parameters = action_parameters

    @property
    def object_id(self) -> str:
        if self._object_id is None:
            raise ValueError("object_idが設定されていません")
        return self._object_id

    @object_id.setter
    def object_id(self, value: str):
        if not isinstance(value, str):
            raise ValueError("object_idは文字列で指定してください")
        self._object_id = value

    @property
    def action(self) -> str:
        if self._action is None:
            raise ValueError("actionが設定されていません")
        return self._action

    @action.setter
    def action(self, value: str):
        if not isinstance(value, str):
            raise ValueError("actionは文字列で指定してください")
        self._action = value

    @property
    def action_parameters(self) -> dict:
        if self._action_parameters is None:
            raise ValueError("action_parametersが設定されていません")
        return self._action_parameters

    @action_parameters.setter
    def action_parameters(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("action_parametersは辞書型で指定してください")
        self._action_parameters = value

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {
            "object_id": self.object_id,
            "action": self.action,
            "action_parameters": self.action_parameters,
        }
        self.command_body = body
        return body


class TransferCommand(CommandBase):
    """
    ファイル転送コマンドを管理するクラス
    """

    def __init__(self, file_path: str | None = None):
        super().__init__(
            command_name="TRANSFER",
        )
        self._file_path = file_path

    @property
    def file_path(self) -> str:
        if self._file_path is None:
            raise ValueError("file_pathが設定されていません")
        return self._file_path

    @file_path.setter
    def file_path(self, value: str):
        if not isinstance(value, str):
            raise ValueError("file_pathは文字列で指定してください")
        if not os.path.exists(value):
            raise FileNotFoundError(f"ファイルが見つかりません: {value}")
        self._file_path = value

    @property
    def file_name(self) -> str:
        return os.path.basename(self.file_path)

    @property
    def file_size(self) -> int:
        return os.path.getsize(self.file_path)

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {
            "file_name": self.file_name,
            "file_size": self.file_size,
        }
        self.command_body = body
        logger.debug(f"ファイル転送コマンドのボディ: {body}")
        return body


class NextCommand(CommandBase):
    """
    次のオブジェクトに変更するコマンド
    """

    def __init__(self):
        super().__init__(
            command_name="NEXT",
        )

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {}
        self.command_body = body
        return body


class PreviousCommand(CommandBase):
    """
    前のオブジェクトに変更するコマンド
    """

    def __init__(self):
        super().__init__(
            command_name="PREVIOUS",
        )

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {}
        self.command_body = body
        return body


class ListCommand(CommandBase):
    """
    オブジェクトリスト取得コマンド
    """

    def __init__(self):
        super().__init__(
            command_name="LIST",
        )

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {}
        self.command_body = body
        return body


class PingCommand(CommandBase):
    """
    Pingコマンド
    """

    def __init__(self):
        super().__init__(
            command_name="PING",
        )

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {}
        self.command_body = body
        return body


class UpdateCommand(CommandBase):
    """
    特定の名前のオブジェクトに変更するコマンド
    """

    def __init__(self, file_name: str | None = None):
        super().__init__(
            command_name="UPDATE",
        )
        self._file_name = file_name

    @property
    def file_name(self) -> str:
        if self._file_name is None:
            raise ValueError("file_nameが設定されていません")
        return self._file_name

    @file_name.setter
    def file_name(self, value: str):
        if not isinstance(value, str):
            raise ValueError("file_nameは文字列で指定してください")
        self._file_name = value

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {
            "file_name": self.file_name,
        }
        self.command_body = body
        return body

class DeleteCommand(CommandBase):
    """
    オブジェクト削除コマンド
    """

    def __init__(self, object_id: str | None = None):
        super().__init__(
            command_name="DELETE",
        )
        self._object_id = object_id

    @property
    def object_id(self) -> str:
        if self._object_id is None:
            raise ValueError("object_idが設定されていません")
        return self._object_id

    @object_id.setter
    def object_id(self, value: str):
        if not isinstance(value, str):
            raise ValueError("object_idは文字列で指定してください")
        self._object_id = value

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {
            "object_id": self.object_id,
        }
        self.command_body = body
        return body

class GetModelCommand(CommandBase):
    """
    モデル取得コマンド
    """

    def __init__(self):
        super().__init__(
            command_name="GET_MODEL",
        )

    def convert_body(self) -> dict:
        """
        コマンドのボディを生成
        """
        body = {}
        self.command_body = body
        return body


class ResponseModel:
    """
    レスポンスモデル
    """

    def __init__(self, header: str, body: dict):
        self._header = header
        self._body = body

    @property
    def header(self) -> str:
        return self._header

    @property
    def body(self) -> dict:
        return self._body

    @classmethod
    def from_str(cls, response_str: str) -> "ResponseModel":
        header, body = response_str.split("\n", 1)
        return cls(header, json.loads(body))
