import logging
from uuid import uuid4

from flet import (
    Page,
)

from app.ai.agent import ChatbotGraph
from app.controller.core import AbstractController
from app.controller.manager.server_manager import ServerManager
from app.models.chat_models import Message, MessageType
from app.views.chat_view import ChatView, create_chat_message

logger = logging.getLogger(__name__)

ERROR_MESSAGE = """
# エラーが発生しました。

再度時間をおいてお試しください。

もしエラーが続く場合は、LLMの設定を確認してください。
"""


class ChatController(AbstractController):
    def __init__(self, page: Page, socket_server: ServerManager):
        super().__init__(page)
        self.server = socket_server
        self._initialize_chatbot()

    def _init_session(self) -> str:
        self.session_id = str(uuid4())
        self.page.session.set("session_id", self.session_id)
        logger.info(f"Session ID set: {self.session_id}")
        return self.session_id

    def _initialize_chatbot(self):
        self.chatbot = ChatbotGraph(server=self.server)
        if not self.page.session.contains_key("session_id"):
            self._init_session()
        else:
            self.session_id = self.page.session.get("session_id")
        self.chatbot.set_memory_config(self.session_id)

    def get_chat_history(self) -> list[Message]:
        chat_history = self.chatbot.graph.get_state(self.chatbot.memory_config)
        try:
            chat_history = chat_history.values["messages"]
            messages = []
            for message in chat_history:
                if message.content == "":
                    continue

                sender = "USER" if "HumanMessage" in str(type(message)) else "AI"
                message_type = MessageType.USER if sender == "USER" else MessageType.AI
                messages.append(Message(name=sender, content=message.content, message_type=message_type))
            return messages
        except KeyError:
            pass
        except Exception as e:
            logger.error(e)

    def tap_link(self, e):
        try:
            int(e.data)
            self.page.go(f"/documents/{e.data}")
        except Exception:
            self.page.launch_url(e.data)

    def _add_message(self, message: Message):
        message_body = create_chat_message(message, self.tap_link)
        self.view.chat_list.controls.append(message_body)

    def add_message(self, message: Message):
        self._add_message(message)
        self.page.update()

    def add_messages(self, messages: list[Message]):
        if not messages:
            return
        for message in messages:
            self._add_message(message)
        self.page.update()

    def send_message(self, _):
        if self.view.text_field.value != "":
            message = self.view.text_field.value
            self.view.text_field.value = ""
            self.view.progress_bar.visible = True
            self.page.update()

            try:
                for response in self.chatbot.stream_graph_updates(message):
                    logger.debug(f"Response: {response}")
                    if "tool_calls" in response.additional_kwargs:
                        # TODO: toolを実行した場合の表示処理を記述する
                        pass
                    else:
                        sender = "USER" if "HumanMessage" in str(type(response)) else "AI"
                        message_type = MessageType.USER if sender == "USER" else MessageType.AI
                        self.add_message(
                            Message(
                                name=sender,
                                content=response.content,
                                message_type=message_type,
                            )
                        )
            except Exception as err:
                logger.error(f"Error sending message: {err}")
                self.add_message(Message(name="AI", content=ERROR_MESSAGE, message_type=MessageType.AI))
            finally:
                self.view.progress_bar.visible = False
                self.view.text_field.focus()
                self.page.update()

    def init_chat_button(self, _):
        self._init_session()
        self._initialize_chatbot()
        self.view.chat_list.controls.clear()
        self.page.update()

    def get_view(self):
        self.view = ChatView(self.session_id, self.send_message, self.init_chat_button)
        self.add_messages(self.get_chat_history())
        return self.view


if __name__ == "__main__":
    import flet as ft

    from app.controller.manager.server_manager import ServerManager
    from app.logging_config import setup_logging

    setup_logging()

    def main(page: Page) -> None:
        page.title = "AI Chat"
        server = ServerManager()
        chat_page = ChatController(page, server)
        page.add(chat_page.get_view())

    ft.app(main)
