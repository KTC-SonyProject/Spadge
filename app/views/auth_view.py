from flet import (
    Colors,
    Column,
    Container,
    CrossAxisAlignment,
    ElevatedButton,
    MainAxisAlignment,
    Page,
    Text,
    TextField,
    alignment,
    border_radius,
)


class BaseAuthView(Column):
    def __init__(self, body_content: list):
        super().__init__(
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            expand=True,
        )

        self.controls = [
            Container(
                content=Column(
                    controls=[
                        *body_content,
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


class LoginView(BaseAuthView):
    def __init__(self, page: Page, login: callable, is_errored: bool):
        self.page = page

        self.error_text = Text(
            "このページ、または機能を行うには認証が必要です。", size=15, color=Colors.RED, visible=is_errored
        )
        self.user_input = TextField(
            label="UserID",
            border_radius=border_radius.all(10),
            bgcolor=Colors.WHITE,
            width=300,
            on_submit=lambda e: login(e, self.user_input.value, self.password_input.value),
        )
        self.password_input = TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border_radius=border_radius.all(10),
            bgcolor=Colors.WHITE,
            width=300,
            on_submit=lambda e: login(e, self.user_input.value, self.password_input.value),
        )
        self.login_button = ElevatedButton(
            text="Login",
            on_click=lambda e: login(e, self.user_input.value, self.password_input.value),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            width=300,
            height=50,
        )
        self.body_content = [
            self.error_text,
            Text("Login", size=30, weight="bold", color=Colors.BLUE),
            self.user_input,
            self.password_input,
            self.login_button,
        ]

        super().__init__(body_content=self.body_content)


class LogoutView(BaseAuthView):
    def __init__(self, page: Page, logout: callable):
        self.page = page
        self.logout_button = ElevatedButton(
            text="Logout",
            on_click=lambda e: logout(e),
            bgcolor=Colors.RED,
            color=Colors.WHITE,
            width=300,
            height=50,
        )
        self.body_content = [
            Text("Logout", size=30, weight="bold", color=Colors.RED),
            self.logout_button,
        ]

        super().__init__(body_content=self.body_content)


class UpdateView(BaseAuthView):
    def __init__(self, page: Page, update: callable, now_id: str):
        self.page = page
        self.user_input = TextField(
            label="UserID",
            border_radius=border_radius.all(10),
            bgcolor=Colors.WHITE,
            width=300,
            value=now_id,
            on_submit=lambda e: update(e, self.user_input.value, self.password_input.value),
        )
        self.password_input = TextField(
            label="Password(パスワードは必ず変更してください)",
            password=True,
            can_reveal_password=True,
            border_radius=border_radius.all(10),
            bgcolor=Colors.WHITE,
            width=300,
            on_submit=lambda e: update(e, self.user_input.value, self.password_input.value),
        )
        self.update_button = ElevatedButton(
            text="Update",
            on_click=lambda e: update(e, self.user_input.value, self.password_input.value),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            width=300,
            height=50,
        )
        self.body_content = [
            Text("Update", size=30, weight="bold", color=Colors.BLUE),
            self.user_input,
            self.password_input,
            self.update_button,
        ]

        super().__init__(self.body_content)
