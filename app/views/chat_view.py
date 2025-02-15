import logging

from flet import (
    CircleAvatar,
    Colors,
    Column,
    Container,
    CrossAxisAlignment,
    ElevatedButton,
    ExpansionTile,
    IconButton,
    Icons,
    ListView,
    MainAxisAlignment,
    Markdown,
    MarkdownExtensionSet,
    ProgressBar,
    Row,
    Text,
    TextField,
    TextButton,
    TileAffinity,
    alignment,
    border,
    padding,
)

from app.models.chat_models import Message, MessageType

logger = logging.getLogger(__name__)


def get_initials(text: str) -> str:
    """
    引数の文字列からイニシャルの頭文字を取得する関数

    Args:
        text (str): ユーザー名

    Returns:
        str: イニシャルの頭文字
    """
    return text[0].upper()


def create_chat_message(message: Message, tap_link: callable) -> Container:
    """
    チャットメッセージのControlを作成する関数

    Args:
        message (Message): 作成するメッセージオブジェクト
        tap_link (callable): リンクをタップしたときのコールバック

    Returns:
        Container: チャットメッセージの Container Control
    """
    body = Container(
        padding=padding.symmetric(horizontal=30, vertical=10),
        content=Row(
            vertical_alignment=CrossAxisAlignment.START,
            alignment=MainAxisAlignment.END if message.message_type == MessageType.USER else MainAxisAlignment.START,
            controls=[
                Column(
                    tight=True,
                    spacing=5,
                    expand=True,
                    horizontal_alignment=CrossAxisAlignment.END if message.message_type == MessageType.USER else None,
                    controls=[
                        Text(message.name, weight="bold", size=20),
                        Markdown(
                            value=message.content,
                            selectable=True,
                            extension_set=MarkdownExtensionSet.GITHUB_FLAVORED,
                            on_tap_link=tap_link,
                            scale=1.5,
                        ),
                    ],
                )
            ],
        ),
    )

    if message.message_type in {MessageType.AI, MessageType.TOOL}:
        body.content.controls.insert(
            0,
            CircleAvatar(
                content=Text(get_initials(message.name)),
                color=Colors.WHITE,
                bgcolor=Colors.BLUE,
            ),
        )

    return body


class ChatMessageTile(ExpansionTile):
    def __init__(self, name: str, content: str, tap_link: callable):
        self.name = Text(name, weight="bold", color=Colors.GREY_500)
        self.body = Markdown(
            value=content,
            selectable=True,
            extension_set=MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=tap_link,
        )
        super().__init__(
            title=self.name,
            affinity=TileAffinity.LEADING,
            text_color=Colors.GREY_500,
            controls=[self.body],
        )


def create_chat_message_tile(name: str, content: str, tap_link: callable) -> ExpansionTile:
    return ChatMessageTile(name, content, tap_link)


class ChatMessageCard(Container):
    def __init__(self, message: Message, tap_link: callable):
        super().__init__(
            padding=padding.symmetric(horizontal=30, vertical=10),
        )
        self.name = Text(message.name, weight="bold")
        self.body = Markdown(
            value=message.content,
            selectable=True,
            extension_set=MarkdownExtensionSet.GITHUB_FLAVORED,
            on_tap_link=tap_link,
        )
        self.thinking_chat = ExpansionTile(
            title=Text("Thinking_flow", color=Colors.GREY_500),
            affinity=TileAffinity.LEADING,
            text_color=Colors.GREY_500,
            controls=[],
            visible=False,
        )
        self.content = Row(
            vertical_alignment=CrossAxisAlignment.START,
            alignment=MainAxisAlignment.END if message.message_type == MessageType.USER else MainAxisAlignment.START,
            controls=[
                Column(
                    tight=True,
                    spacing=5,
                    expand=True,
                    horizontal_alignment=CrossAxisAlignment.END if message.message_type == MessageType.USER else None,
                    controls=[
                        self.name,
                        self.thinking_chat,
                        self.body,
                    ],
                )
            ],
        )

        if message.message_type in {MessageType.AI, MessageType.TOOL}:
            self.content.controls.insert(
                0,
                CircleAvatar(
                    content=Text(get_initials(message.name)),
                    color=Colors.WHITE,
                    bgcolor=Colors.BLUE,
                ),
            )


def create_chat_header(session_id: str, init_chat_button: callable) -> Container:
    return Container(
        padding=10,
        alignment=alignment.center,
        content=Row(
            spacing=20,
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            wrap=True,
            controls=[
                Text(f"現在のセッションID: {session_id}", size=10),
                ElevatedButton("会話を初期化する", on_click=init_chat_button),
            ],
        ),
    )

def create_example_prompt(text: str, prompt: str, on_click: callable) -> TextButton:
    return TextButton(
        text=text,
        on_click=lambda _: on_click(prompt),
    )


class ChatView(Column):
    """
    チャット画面のView

    Args:
        session_id (str): セッションID
        send_message_click (callable): メッセージ送信ボタンをクリックしたときのコールバック
        init_chat_button (callable): チャットを初期化するボタンをクリックしたときのコールバック
        example_prompts (list[TextButton]): ユーザーが選択できる例のプロンプトリスト

    Attributes:
        chat_list (ListView): チャットメッセージのリスト
        text_field (TextField): メッセージ入力欄
        progress_bar (ProgressBar): メッセージ送信中のプログレスバー
    """

    def __init__(
            self,
            session_id: str,
            send_message_click: callable,
            init_chat_button: callable,
            example_prompts: list[TextButton]
        ):
        super().__init__(
            expand=True,
        )
        self.chat_list = ListView(expand=True, spacing=50, auto_scroll=True)
        self.text_field = TextField(
            hint_text="Write a message...",
            autocorrect=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=send_message_click,
        )
        self.progress_bar = ProgressBar(color=Colors.BLUE, bgcolor=Colors.GREY_200, visible=False)

        self.controls = [
            create_chat_header(session_id, init_chat_button),
            Container(
                content=self.chat_list,
                border=border.all(1, Colors.OUTLINE),
                border_radius=5,
                expand=True,
            ),
            Row(
                controls=example_prompts,
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER,
                spacing=10,
                wrap=True,
            ),
            self.progress_bar,
            Row(
                controls=[
                    self.text_field,
                    IconButton(icon=Icons.SEND_ROUNDED, tooltip="Send message", on_click=send_message_click),
                ]
            ),
        ]
