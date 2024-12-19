from flet import (
    Page,
    Row,
)

from app.controller.layout import MyLayout


class MyView(Row):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        self.page.go(self.page.route)

    def route_change(self, route):
        self.page.views.clear()
        self.page.views.append(MyLayout(self.page, self.page.route))
        self.page.update()

    def view_pop(self, view):
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)
