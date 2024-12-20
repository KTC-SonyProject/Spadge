from dataclasses import dataclass

from app.controller.core import go_page


@dataclass
class HomeCardItem:
    """
    ホーム画面のカードアイテムを表すデータクラス。

    Attributes:
        title (str): カードのタイトル。
        subtitle (str): カードのサブタイトル。
        icon (str): カードのアイコン。
        go_page (go_page): カードをクリックした際に遷移するページの関数。
    """

    title: str
    subtitle: str
    icon: str
    go_page: go_page
