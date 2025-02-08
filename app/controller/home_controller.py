from flet import (
    Icons,
    Page,
    app,
)

from app.controller.core import AbstractController
from app.controller.manager.auth_manager import AuthManager
from app.models.home_models import HomeCardItem, go_page
from app.views.home_view import HomeCard, HomeCardList, HomeView


class HomeController(AbstractController):
    def __init__(self, page: Page, auth_manager: AuthManager):
        super().__init__(page)

        self.auth_manager = auth_manager

        self.HOME_CARD_ITEMS = [
            HomeCardItem(
                title="Chat",
                subtitle="AIとチャットを通じて展示物の情報について質問したり、画面の操作を行うことができます。",
                icon=Icons.CHAT,
                go_page=go_page(self.page, "/chat"),
            ),
            HomeCardItem(
                title="Documents",
                subtitle="展示物の情報を閲覧することができます。",
                icon=Icons.DESCRIPTION,
                go_page=go_page(self.page, "/documents"),
            ),
            HomeCardItem(
                title="Unity",
                subtitle="Unityアプリケーションを操作することができます。",
                icon=Icons.CODE,
                go_page=go_page(self.page, "/unity"),
            ),
        ]
        if self.auth_manager.check_is_authenticated():
            self.HOME_CARD_ITEMS[1].subtitle = "展示物の情報を閲覧・編集・削除することができます。"
            self.HOME_CARD_ITEMS.append(
                HomeCardItem(
                    title="Settings",
                    subtitle="アプリケーションの設定を変更することができます。",
                    icon=Icons.SETTINGS,
                    go_page=go_page(self.page, "/settings"),
                )
            )

    def _create_home_card(self, card_items: list[HomeCardItem]) -> list[HomeCard]:
        items = []

        for card_item in card_items:
            items.append(HomeCard(card_item))

        return items

    def _get_home_card_list(self) -> HomeCardList:
        return HomeCardList(self._create_home_card(self.HOME_CARD_ITEMS))

    def get_view(self) -> HomeView:
        return HomeView(self._get_home_card_list())


if __name__ == "__main__":

    def main(page: Page) -> None:
        page.title = "test"
        home_controller = HomeController(page)
        home_view = home_controller.get_home_view()
        page.add(home_view)

    app(main)
