from flet import (
    Column,
    Container,
    Divider,
    Dropdown,
    ElevatedButton,
    Row,
    Text,
    alignment,
    dropdown,
)

from app.views.core import (
    BaseTabBodyView,
    TabView,
    create_switch,
    create_tabs,
    create_text_field,
)


class BaseSettingsView(BaseTabBodyView):
    def __init__(self, title: str, body_content: any):
        super().__init__(title, body_content)


def visible_body_column(visible: bool, controls: list) -> Column:
    return Column(
        visible=visible,
        controls=controls,
    )


class GeneralSettingsView(BaseSettingsView):
    def __init__(self, body_content: any):
        super().__init__("General Settings", body_content)


class DatabaseSettingsView(BaseSettingsView):
    def __init__(self, body_content: any):
        super().__init__("Database Settings", body_content)


def create_llm_settings_body():
    return Column(
        spacing=20,
        controls=[
            Dropdown(
                label="LLM Provider",
                value="azure",
                options=[
                    dropdown.Option("azure"),
                    dropdown.Option("gemini"),
                    dropdown.Option("ollama"),
                ],
            ),
            Column(
                controls=[
                    create_text_field(
                        label="Endpoint",
                        value="",
                    ),
                    create_text_field(
                        label="API Key",
                        value="",
                        password=True,
                        can_reveal_password=True,
                    ),
                    create_text_field(
                        label="Deployment Name",
                        value="",
                    ),
                    create_text_field(
                        label="Deployment Embedding Name",
                        value="",
                    ),
                    create_text_field(
                        label="API Version",
                        value="",
                    ),
                ]
            ),
            Divider(),
            create_switch(
                label="Use LangSmith",
                value=False,
            ),
            Column(
                controls=[
                    create_text_field(
                        label="Project Name",
                        value="",
                    ),
                    create_text_field(
                        label="LangSmith API Key",
                        value="",
                        password=True,
                        can_reveal_password=True,
                    ),
                ]
            ),
        ],
    )


class LLMSettingsView(BaseSettingsView):
    def __init__(self, body_content: any):
        super().__init__("LLM Settings", body_content)


class SettingsView(Column):
    def __init__(self, tabs: list[TabView], save_button_click: callable):
        super().__init__(
            spacing=10,
            expand=True,
            # scroll=True,
        )

        title = Container(
            padding=10,
            alignment=alignment.center,
            content=Row(
                spacing=20,
                controls=[
                    Text("Settings", size=30),
                    ElevatedButton("Save Settings", on_click=save_button_click),
                ],
            ),
        )

        self.controls = [
            title,
            create_tabs(tabs),
        ]
