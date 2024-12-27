from flet import (
    Column,
    Page,
    Text,
)


class TemplateView(Column):
    def __init__(self, page: Page, text: str = "Body Text"):
        super().__init__()
        self.text = text
        self.spacing = 10
        self.controls = [
            Text("**********************"),
            Text(self.text),
            Text("**********************"),
        ]
