"""
View用の共通基底クラスや抽象クラスを定義
"""

import logging
import time

from flet import (
    AlertDialog,
    Banner,
    Column,
    Container,
    Control,
    Divider,
    Dropdown,
    IconButton,
    Icons,
    MainAxisAlignment,
    Page,
    Switch,
    Tab,
    TabAlignment,
    Tabs,
    Text,
    TextField,
    alignment,
    dropdown,
    padding,
)

logger = logging.getLogger(__name__)


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


def create_banner(status, message, close_banner):
    """バナーメッセージを作成する"""
    banner = Banner(
        bgcolor="red" if status == "error" else "green",
        content=Text(message),
        actions=[IconButton(icon=Icons.CLOSE, on_click=close_banner)],
    )
    return banner


class BaseTabBodyView(Column):
    """
    タブのボディ部分の基底クラス
    """

    def __init__(self, title: str, body_content: any):
        super().__init__(
            spacing=10,
            expand=True,
            scroll=True,
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
                ),
            ],
        )


class TabView(Tab):
    def __init__(self, title: str, content: BaseTabBodyView):
        super().__init__(
            text=title,
            content=content,
        )


def create_tabs(tabs: list[TabView]):
    return Tabs(
        expand=True,
        selected_index=0,
        animation_duration=300,
        tab_alignment=TabAlignment.CENTER,
        tabs=tabs,
    )


class BannerView:
    def __init__(self, page: Page):
        self.page = page
        self.banner = None

    def close_banner(self, _):
        self.banner.open = False
        self.page.update()

    def show_banner(self, status, message):
        self.banner = create_banner(status, message, self.close_banner)
        self.page.overlay.append(self.banner)
        self.banner.open = True
        self.page.update()
        time.sleep(2)
        self.close_banner(None)


def create_modal(
    title: Control,
    content: Control,
    actions: list[Control],
    actions_alignment: MainAxisAlignment = MainAxisAlignment.END,
):
    return AlertDialog(
        modal=True,
        inset_padding=padding.symmetric(vertical=40, horizontal=100),
        title=title,
        content=content,
        actions=actions,
        actions_alignment=actions_alignment,
    )
