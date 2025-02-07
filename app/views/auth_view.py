from flet import (
    Column,
    ElevatedButton,
    Page,
    TextField,
)


class AuthView(Column):
    def __init__(self, page: Page, login: callable):
        super().__init__(
            spacing=10,
        )

        self.user_input = TextField(label="Username")
        self.password_input = TextField(label="Password", password=True)
        self.login_button = ElevatedButton(
            text="Login", on_click=lambda e: login(e, self.user_input.value, self.password_input.value)
        )

        self.controls = [
            self.user_input,
            self.password_input,
            self.login_button,
        ]
