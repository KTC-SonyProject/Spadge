"""
View用の共通基底クラスや抽象クラスを定義
"""

import logging

from flet import (
    Banner,
    Column,
    Container,
    Divider,
    Dropdown,
    IconButton,
    Icons,
    Switch,
    Tab,
    Text,
    TextField,
    alignment,
    dropdown,
)

logger = logging.getLogger(__name__)




class BaseTabBodyView(Column):
    """
    タブのボディ部分の基底クラス
    """
    def __init__(self, title: str, body_content: any):
        super().__init__(
            spacing=10,
            expand=True,
            alignment=alignment.center,
            controls=[
                Container(
                    padding=10,
                    alignment=alignment.center,
                    content=Text(title, size=30),
                ),
                Divider(),
                Column(
                    controls=body_content,
                    expand=True,
                )
            ]
        )

class TabView(Tab):
    def __init__(self, title: str, content: BaseTabBodyView):
        super().__init__(
            text=title,
            content=content,
        )


def create_text_field(label, value, on_change, password=False, can_reveal_password=False):
    """共通のTextField作成関数"""
    return TextField(
        label=label,
        value=value,
        on_change=on_change,
        password=password,
        can_reveal_password=can_reveal_password,
    )

def create_switch(label, value, on_change):
    """共通のSwitch作成関数"""
    return Switch(
        label=label,
        value=value,
        on_change=on_change,
    )

def create_dropdown(label, value, items, on_change):
    """共通のDropdown作成関数"""
    options = [dropdown.Option(item) for item in items]
    return Dropdown(
        label=label,
        value=value,
        options=options,
        on_change=on_change,
    )

def banner_message(status, message, close_banner):
    """バナーメッセージを表示する"""
    banner = Banner(
        bgcolor="red" if status == "error" else "green",
        content=Text(message),
        actions=[IconButton(icon=Icons.CLOSE, on_click=close_banner)],
    )
    return banner
