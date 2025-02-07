from flet import (
    Column,
    Container,
    ElevatedButton,
    Page,
    Text,
    TextField,
    alignment,
    border_radius,
    Colors,
    MainAxisAlignment,
    CrossAxisAlignment,
)


class AuthView(Column):
    def __init__(self, page: Page, login: callable, is_errored: bool):
        super().__init__(
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            expand=True,
        )

        self.error_text = Text(
            "このページ、または機能を行うには認証が必要です。", size=15, color=Colors.RED, visible=is_errored
        )

        self.user_input = TextField(
            label="Username",
            border_radius=border_radius.all(10),
            bgcolor=Colors.WHITE,
            width=300,
        )
        self.password_input = TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border_radius=border_radius.all(10),
            bgcolor=Colors.WHITE,
            width=300,
        )
        self.login_button = ElevatedButton(
            text="Login",
            on_click=lambda e: login(e, self.user_input.value, self.password_input.value),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            width=300,
            height=50,
        )

        self.controls = [
            Container(
                content=Column(
                    controls=[
                        self.error_text,
                        Text("Login", size=30, weight="bold", color=Colors.BLUE),
                        self.user_input,
                        self.password_input,
                        self.login_button,
                    ],
                    spacing=20,
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                padding=20,
                border_radius=10,
                width=350,
                alignment=alignment.center,
                expand=True,
            )
        ]


class LogoutView(Column):
    def __init__(self, page: Page, logout: callable):
        super().__init__(
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            expand=True,
        )

        self.logout_button = ElevatedButton(
            text="Logout",
            on_click=lambda e: logout(e),
            bgcolor=Colors.RED,
            color=Colors.WHITE,
            width=300,
            height=50,
        )

        self.controls = [
            Container(
                content=Column(
                    controls=[
                        Text("Logout", size=30, weight="bold", color=Colors.RED),
                        self.logout_button,
                    ],
                    spacing=20,
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                padding=20,
                border_radius=10,
                width=350,
                alignment=alignment.center,
                expand=True,
            )
        ]
