from flet import (
    CircleAvatar,
    Colors,
    Column,
    Container,
    ControlEvent,
    CrossAxisAlignment,
    IconButton,
    Icons,
    ListView,
    MainAxisAlignment,
    Markdown,
    MarkdownExtensionSet,
    Page,
    ProgressBar,
    Row,
    Text,
    TextField,
    app,
    border,
    padding,
)

from app.ai.agent import ChatbotGraph


class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type


# アイコン、名前、チャットの再利用可能なチャットメッセージ
class ChatMessage(Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = CrossAxisAlignment.START
        if message.message_type == "ai":
            self.alignment = MainAxisAlignment.START
            self.controls = [
                # アイコン
                CircleAvatar(
                    content=Text(self.get_initials(message.user_name)),
                    color=Colors.WHITE,
                    bgcolor=self.get_avatar_color(message.user_name),
                ),
                # 名前とメッセージのカラム
                Column(
                    [
                        Text(message.user_name, weight="bold"),
                        Markdown(
                            value=message.text,
                            selectable=True,
                            extension_set=MarkdownExtensionSet.GITHUB_WEB,
                            on_tap_link=self.tap_link,
                        ),
                    ],
                    tight=True,
                    spacing=5,
                    expand=True,
                ),
            ]
        else:
            self.alignment = MainAxisAlignment.END
            self.controls = [
                # 名前とメッセージのカラム
                Column(
                    [
                        Text(message.user_name, weight="bold"),
                        Markdown(
                            value=message.text,
                            selectable=True,
                            extension_set=MarkdownExtensionSet.GITHUB_WEB,
                            on_tap_link=self.tap_link,
                        ),
                    ],
                    tight=True,
                    spacing=5,
                    expand=True,
                    horizontal_alignment=CrossAxisAlignment.END,
                ),
                # # アイコン
                # CircleAvatar(
                #     content=Text(self.get_initials(message.user_name)),
                #     color=Colors.WHITE,
                #     bgcolor=self.get_avatar_color(message.user_name)
                # ),
            ]

    # ユーザ名の頭文字の取得
    def get_initials(self, user_name: str) -> str:
        return user_name[:1].capitalize()

    # ユーザ名に基づきハッシュを使いアイコンの色をランダムに決める
    def get_avatar_color(self, user_name: str) -> Colors:
        Colors_lookup = [
            Colors.AMBER,
            Colors.BLUE,
            Colors.BROWN,
            Colors.CYAN,
            Colors.GREEN,
            Colors.INDIGO,
            Colors.LIME,
            Colors.ORANGE,
            Colors.PINK,
            Colors.PURPLE,
            Colors.RED,
            Colors.TEAL,
            Colors.YELLOW,
        ]
        return Colors_lookup[hash(user_name) % len(Colors_lookup)]

    def tap_link(self, e: ControlEvent) -> None:
        try:
            int(e.data)
            self.page.go(f"/documents/{e.data}")
        except Exception:
            self.page.launch_url(e.data)


class ChatBody(Column):
    def __init__(self, page: Page, socket_server, session_id: str = "1"):
        super().__init__()
        self.page = page
        try:
            self._initialize_chatbot(session_id, socket_server)
        except ValueError as e:
            self.controls = [
                Container(
                    content=Text(str(e), color=Colors.RED),
                    padding=padding.all(20),
                )
            ]
            return
        self.chat = ListView(expand=True, spacing=50, auto_scroll=True)
        self.new_message = TextField(
            hint_text="Write a message...",
            autocorrect=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=self.send_message_click,
        )
        self.progress = ProgressBar(color=Colors.PINK, bgcolor=Colors.GREY_200, visible=False)
        self.controls = [
            Container(
                content=self.chat,
                border=border.all(1, Colors.OUTLINE),
                border_radius=5,
                expand=True,  # Containerも縦に展開する
            ),
            self.progress,
            Row(
                [
                    self.new_message,
                    IconButton(icon=Icons.SEND_ROUNDED, tooltip="Send message", on_click=self.send_message_click),
                ]
            ),
        ]
        self.expand = True
        self.show_chat_history()

    def _initialize_chatbot(self, session_id, socket_server) -> None:
        self.chatbot_graph = ChatbotGraph(server=socket_server, verbose=True)
        self.session_id = session_id
        self.chatbot_graph.set_memory_config(self.session_id)

    def show_chat_history(self) -> None:
        chat_history = self.chatbot_graph.graph.get_state(self.chatbot_graph.memory_config)
        try:
            messages_list = chat_history.values["messages"]
            for message in messages_list:
                if message.content == "":
                    continue
                if message.content is list:
                    tool_results = message.content
                    urls = [f"- [{result['title']}]({result['url']})" for result in tool_results]
                    urls_message = "\n".join(urls)
                    self.on_message(
                        Message(
                            user_name="AI", text=f"ツールを使用して取得した情報です:\n{urls_message}", message_type="ai"
                        )
                    )
                else:
                    sender = "User" if "HumanMessage" in str(type(message)) else "AI"
                    message_type = "human" if "HumanMessage" in str(type(message)) else "ai"
                    self.on_message(Message(user_name=sender, text=message.content, message_type=message_type))
        except KeyError:
            pass
        except Exception as e:
            print(e)

    def on_message(self, message: Message) -> None:
        m = Container(content=ChatMessage(message), padding=padding.symmetric(horizontal=30, vertical=10))
        self.chat.controls.append(m)
        self.page.update()

    def send_message_click(self, e: ControlEvent) -> None:
        if self.new_message.value != "":
            # self.on_message(Message(user_name='user', text=self.new_message.value, message_type='human'))
            send_message = self.new_message.value
            self.new_message.value = ""
            self.progress.visible = True
            self.page.update()
            tool_used = False

            try:
                for response in self.chatbot_graph.stream_graph_updates(send_message):
                    print(response)
                    # もしresponseのadditional_kwargs{}が'tool_calls'を持っていたら、それを表示する
                    if "tool_calls" in response.additional_kwargs:
                        tool_used = True
                    elif tool_used and "results" in response.content:
                        tool_results = response.content
                        urls = [f"- [{result['title']}]({result['url']})" for result in tool_results]
                        urls_message = "\n".join(urls)
                        self.on_message(
                            Message(
                                user_name="AI",
                                text=f"ツールを使用して取得した情報です:\n{urls_message}",
                                message_type="ai",
                            )
                        )
                        tool_used = False
                    else:
                        sender = "user" if "HumanMessage" in str(type(response)) else "AI"
                        message_type = "human" if "HumanMessage" in str(type(response)) else "ai"
                        self.on_message(Message(user_name=sender, text=response.content, message_type=message_type))
            except Exception as error:
                print(error)
                sender = "AI"
                message_type = "ai"
                error_message = """
# エラーが発生しました。

再度時間をおいてお試しください。

もしエラーが続く場合は、LLMの設定を確認してください。
"""
                self.on_message(Message(user_name=sender, text=error_message, message_type=message_type))

            self.progress.visible = False
            self.new_message.focus()
            self.page.update()


if __name__ == "__main__":

    def main(page: Page) -> None:
        page.title = "AI Chat"
        chat_page = ChatBody(page)
        page.add(chat_page)

    app(main)
