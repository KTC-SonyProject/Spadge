import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# class Message:
#     def __init__(self, user_name: str, text: str, message_type: str):
#         self.user_name = user_name
#         self.text = text
#         self.message_type = message_type


class MessageType(Enum):
    """
    メッセージの種類を表すEnum

    Args:
        Enum (_type_): Enumの型
    """

    AI = "ai"
    TOOL = "tool"
    USER = "user"


@dataclass
class Message:
    """
    チャットメッセージのデータクラス

    Args:
        user_name (str): ユーザー名
        text (str): メッセージ
        message_type (MessageType): メッセージの種類
    """

    name: str
    content: str
    message_type: MessageType = MessageType.USER
