import logging
from uuid import uuid4

from flet import (
    Page,
)

from app.controller.core import AbstractController
from app.controller.manager import (
    ObjectDatabaseManager,
    ObjectManager,
    ServerManager,
    SettingsManager,
)
from app.controller.manager.agent_manager import (
    DisplayInfoTool,
    ModelChangeTool,
    ModelListTool,
    SupervisorAgent,
    sub_agents_with_generic,
)
from app.models.chat_models import Message, MessageType
from app.models.database_models import DatabaseHandler
from app.views.chat_view import ChatMessageCard, ChatView, create_chat_message_tile

logger = logging.getLogger(__name__)

ERROR_MESSAGE = """
## エラーが発生しました。

再度時間をおいてお試しください。

もしエラーが続く場合は、LLMの設定を確認してください。
"""


class ChatController(AbstractController):
    def __init__(
        self,
        page: Page,
        socket_server: ServerManager,
        settings_manager: SettingsManager,
        obj_manager: ObjectManager,
        obj_database_manager: ObjectDatabaseManager,
    ):
        super().__init__(page)
        self.server = socket_server
        self.settings_manager = settings_manager
        self.obj_manager = obj_manager
        self.obj_database_manager = obj_database_manager
        if not self.page.session.contains_key("session_id"):
            self._init_session()
        else:
            self.session_id = self.page.session.get("session_id")
        self.agent = self._initialize_agent()

    def _init_session(self) -> str:
        self.session_id = str(uuid4())
        self.page.session.set("session_id", self.session_id)
        logger.info(f"Session ID set: {self.session_id}")
        return self.session_id

    def _initialize_agent(self):
        agent = SupervisorAgent(
            sub_agents_with_generic,
            settings_manager=self.settings_manager,
            thread_id=self.session_id,
        )
        # ここにDisplayAgentに全てのツールを登録しなおす
        agent.sub_agents[0].rebind_tools(
            [
                DisplayInfoTool(dammy_model="NAO"),
                ModelChangeTool(obj_manager=self.obj_manager),
                ModelListTool(obj_database_manager=self.obj_database_manager),
            ]
        )
        return agent

    def get_chat_history(self) -> list[Message]:
        # chat_history = self.chatbot.graph.get_state(self.chatbot.memory_config)
        chat_history = self.agent.graph.get_state(self.agent.memory_config)
        logger.debug(f"\n\n\nChat history: {chat_history}\n\n\n")
        try:
            chat_history = chat_history.values["messages"]
            messages = []
            for message in chat_history:
                if message.content == "":
                    continue

                if message.name:
                    logger.debug(f"Message name: {message.name}, from {message}")
                    sender = f"AI ({message.name})"
                else:
                    logger.debug(f"Message name: user, from {message}")
                    sender = "USER"
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
        message_body = ChatMessageCard(message, self.tap_link)
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
                # for response in self.chatbot.stream_graph_updates(message):
                #     logger.debug(f"Response: {response}")
                #     if "tool_calls" in response.additional_kwargs:
                #         # TODO: toolを実行した場合の表示処理を記述する
                #         pass
                #     else:
                #         sender = "USER" if "HumanMessage" in str(type(response)) else "AI"
                #         message_type = MessageType.USER if sender == "USER" else MessageType.AI
                #         self.add_message(
                #             Message(
                #                 name=sender,
                #                 content=response.content,
                #                 message_type=message_type,
                #             )
                #         )
                # まず今回のメッセージ用UIを作成
                self.add_message(  # ユーザーのメッセージ
                    Message(
                        name="USER",
                        content=message,
                        message_type=MessageType.USER,
                    )
                )
                self.add_message(  # AIのメッセージ
                    Message(
                        name="AI",
                        content="thinking...",
                        message_type=MessageType.AI,
                    )
                )

                for res, metadata in self.agent.stream(message):
                    if res.content and any(agent.name in metadata.get("tags", []) for agent in sub_agents_with_generic):
                        if self.view.chat_list.controls[-1].body.value == "thinking...":
                            logger.debug(f"AI response: {res}, metadata: {metadata.get('tags')[0]}")
                            self.view.chat_list.controls[-1].name.value = f"AI ({metadata.get('tags')[0]})"
                            self.view.chat_list.controls[-1].body.value = res.content
                        elif self.view.chat_list.controls[-1].name.value != f"AI ({metadata.get('tags')[0]})":
                            history_tile = create_chat_message_tile(
                                self.view.chat_list.controls[-1].name.value,
                                self.view.chat_list.controls[-1].body.value, self.tap_link,
                            )
                            self.view.chat_list.controls[-1].thinking_chat.controls.append(history_tile)
                            self.view.chat_list.controls[-1].thinking_chat.visible = True
                            self.view.chat_list.controls[-1].name.value = f"AI ({metadata.get('tags')[0]})"
                            self.view.chat_list.controls[-1].body.value = res.content
                        else:
                            self.view.chat_list.controls[-1].body.value += res.content
                        self.view.chat_list.update()
            except Exception as err:
                logger.error(f"Error sending message: {err}")
                self.add_message(Message(name="AI", content=ERROR_MESSAGE, message_type=MessageType.AI))
            finally:
                self.view.progress_bar.visible = False
                self.view.text_field.focus()
                self.page.update()

    def init_chat_button(self, _):
        self._init_session()
        self._initialize_agent()
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
        settings_manager = SettingsManager()
        db_handler = DatabaseHandler(settings_manager)
        server = ServerManager()
        obj_database_manager = ObjectDatabaseManager(db_handler)
        obj_manager = ObjectManager(obj_database_manager, server)
        chat_page = ChatController(page, server, settings_manager, obj_manager, obj_database_manager)
        page.add(chat_page.get_view())

    ft.app(main)
