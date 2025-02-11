from flet import (
    Card,
    Column,
    Container,
    Icon,
    ListTile,
    MainAxisAlignment,
    Row,
    Text,
    TextButton,
    alignment,
)

from app.models.home_models import HomeCardItem


class HomeCard(Card):
    def __init__(self, card_item: HomeCardItem):
        super().__init__(
            content=Container(
                content=Column(
                    [
                        ListTile(
                            leading=Icon(card_item.icon),
                            title=Text(card_item.title, font_family="bold", weight="bold", size=20),
                            subtitle=Text(card_item.subtitle),
                        ),
                        Row(
                            [TextButton("Go Page", on_click=card_item.go_page)],
                            alignment=MainAxisAlignment.END,
                        ),
                    ]
                ),
                width=500,
                padding=10,
            )
        )


class HomeCardList(Column):
    def __init__(self, card_list: list[HomeCardItem]):
        super().__init__(
            expand=True,
            alignment=MainAxisAlignment.CENTER,
            controls=card_list,
            scroll=True,
        )


class HomeView(Container):
    def __init__(self, home_card_list: HomeCardList):
        super().__init__(
            alignment=alignment.center,
            expand=True,
            content=home_card_list,
        )
