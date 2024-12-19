
from flet import (
    Column,
    Container,
    Divider,
    Dropdown,
    ElevatedButton,
    Row,
    TabAlignment,
    Tabs,
    Text,
    alignment,
    dropdown,
)

from app.views.core import BaseTabBodyView, TabView, create_switch, create_text_field

# class BaseSettingsView(Column):
#     def __init__(self, title: str, settings_manager: SettingsManager, nested_keys: str = ""):
#         super().__init__()
#         self.title = title
#         self.settings_manager = settings_manager
#         self.nested_keys = nested_keys

#         self.expand = True
#         self.controls = [
#             Container(
#                 padding=10,
#                 alignment=alignment.center,
#                 content=Text(title, size=30),
#             ),
#             Divider(),
#             self.create_settings_controls(),
#         ]

#     def create_settings_controls(self):
#         """サブクラスで具体的なコントロールを実装"""
#         return Column()

#     def get_settings_for_keys(self, key: str):
#         """事前に省略用に指定されたkeyと組み合わせて設定を取得"""
#         if self.nested_keys:
#             key = f"{self.nested_keys}.{key}"
#         return self.settings_manager.get_setting(key)

#     def on_change(self, key: str, update_ui: callable = None):
#         """
#         汎用的な on_change 関数。

#         Args:
#             key (str): 更新対象の設定キー。
#             update_ui (callable, optional): UIを更新するための追加処理。
#         """
#         if self.nested_keys:
#             key = f"{self.nested_keys}.{key}"

#         def handler(e):
#             # 設定を更新
#             self.settings_manager.update_setting(key, e.control.value)
#             # UIを更新する必要があれば実行
#             if update_ui:
#                 update_ui(e)

#         return handler


class BaseSettingsView(BaseTabBodyView):
    def __init__(self, title: str, body_content: any):
        super().__init__(title, body_content)


def visible_body_column(visible: bool, controls: list) -> Column:
    return Column(
        visible=visible,
        controls=controls,
    )


# class GeneralSettingsView(BaseSettingsView):
#     def __init__(self, settings_manager: SettingsManager):
#         super().__init__("General Settings", settings_manager, "general_settings")

#     def create_settings_controls(self):
#         return Column(
#             spacing=20,
#             controls=[
#                 create_text_field(
#                     label="App Name",
#                     value=self.get_settings_for_keys("app_name"),
#                     on_change=self.on_change("app_name"),
#                 ),
#                 create_text_field(
#                     label="App Description",
#                     value=self.get_settings_for_keys("app_description"),
#                     on_change=self.on_change("app_description"),
#                 ),
#             ],
#         )

class GeneralSettingsView(BaseSettingsView):
    def __init__(self, body_content: any):
        super().__init__("General Settings", body_content)

# class DatabaseSettingsView(BaseSettingsView):
#     def __init__(self, settings_manager: SettingsManager):
#         super().__init__("Database Settings", settings_manager, "database_settings")

#     def create_settings_controls(self):
#         self.postgres_settings_column = Column(
#             visible=self.get_settings_for_keys("use_postgres"),
#             controls=[
#                 create_text_field(
#                     label="Host",
#                     value=self.get_settings_for_keys("postgres_settings.host"),
#                     on_change=self.on_change("postgres_settings.host"),
#                 ),
#                 create_text_field(
#                     label="Port",
#                     value=self.get_settings_for_keys("postgres_settings.port"),
#                     on_change=self.on_change("postgres_settings.port"),
#                 ),
#                 create_text_field(
#                     label="Database",
#                     value=self.get_settings_for_keys("postgres_settings.database"),
#                     on_change=self.on_change("postgres_settings.database"),
#                 ),
#                 create_text_field(
#                     label="User",
#                     value=self.get_settings_for_keys("postgres_settings.user"),
#                     on_change=self.on_change("postgres_settings.user"),
#                 ),
#                 create_text_field(
#                     label="Password",
#                     value=self.get_settings_for_keys("postgres_settings.password"),
#                     password=True,
#                     can_reveal_password=True,
#                     on_change=self.on_change("postgres_settings.password"),
#                 ),
#             ],
#         )

#         print(self.get_settings_for_keys("use_postgres"))

#         return Column(
#             spacing=20,
#             controls=[
#                 create_switch(
#                     label="Use PostgreSQL",
#                     value=self.get_settings_for_keys("use_postgres"),
#                     on_change=self.on_change(
#                         "use_postgres",
#                         update_ui=self.toggle_postgres_settings_visibility,
#                     ),
#                 ),
#                 self.postgres_settings_column,
#             ],
#         )

#     def toggle_postgres_settings_visibility(self, e):
#         """PostgreSQL設定の表示・非表示を切り替える"""
#         self.postgres_settings_column.visible = e.control.value
#         self.page.update()

class DatabaseSettingsView(BaseSettingsView):
    def __init__(self, body_content: any):
        super().__init__("Database Settings", body_content)


# class LLMSettingsView(BaseSettingsView):
#     def __init__(self, settings_manager: SettingsManager):
#         super().__init__("LLM Settings", settings_manager, "llm_settings")
#         self.expand = True

#     def create_settings_controls(self):
#         self.llm_provider_column = self.get_provider_specific_controls(self.get_settings_for_keys("llm_provider"))

#         self.langsmith_column = Column(
#             visible=self.get_settings_for_keys("use_langsmith"),
#             controls=[
#                 create_text_field(
#                     label="Project Name",
#                     value=self.get_settings_for_keys("langsmith_settings.project_name"),
#                     on_change=self.on_change("langsmith_settings.project_name"),
#                 ),
#                 create_text_field(
#                     label="LangSmith API Key",
#                     value=self.get_settings_for_keys("langsmith_settings.api_key"),
#                     password=True,
#                     can_reveal_password=True,
#                     on_change=self.on_change("langsmith_settings.api_key"),
#                 ),
#             ],
#         )

#         return Column(
#             spacing=20,
#             controls=[
#                 Dropdown(
#                     label="LLM Provider",
#                     value=self.get_settings_for_keys("llm_provider"),
#                     options=[
#                         dropdown.Option("azure"),
#                         dropdown.Option("gemini"),
#                         dropdown.Option("ollama"),
#                     ],
#                     on_change=self.on_change(
#                         "llm_provider",
#                         update_ui=self.update_provider_controls,
#                     ),
#                 ),
#                 self.llm_provider_column,
#                 Divider(),
#                 create_switch(
#                     label="Use LangSmith",
#                     value=self.get_settings_for_keys("use_langsmith"),
#                     on_change=self.on_change(
#                         "use_langsmith",
#                         update_ui=self.toggle_langsmith_settings_visibility,
#                     ),
#                 ),
#                 self.langsmith_column,
#             ],
#         )

    # def get_provider_specific_controls(self, provider: str):
    #     """プロバイダーごとの設定コントロールを返す"""
    #     if provider == "azure":
    #         return Column(
    #             controls=[
    #                 create_text_field(
    #                     label="Endpoint",
    #                     value=self.get_settings_for_keys("azure_llm_settings.endpoint"),
    #                     on_change=self.on_change("azure_llm_settings.endpoint"),
    #                 ),
    #                 create_text_field(
    #                     label="API Key",
    #                     value=self.get_settings_for_keys("azure_llm_settings.api_key"),
    #                     password=True,
    #                     can_reveal_password=True,
    #                     on_change=self.on_change("azure_llm_settings.api_key"),
    #                 ),
    #                 create_text_field(
    #                     label="Deployment Name",
    #                     value=self.get_settings_for_keys("azure_llm_settings.deployment_name"),
    #                     on_change=self.on_change("azure_llm_settings.deployment_name"),
    #                 ),
    #                 create_text_field(
    #                     label="Deployment Embedding Name",
    #                     value=self.get_settings_for_keys("azure_llm_settings.deployment_embedding_name"),
    #                     on_change=self.on_change("azure_llm_settings.deployment_embedding_name"),
    #                 ),
    #                 create_text_field(
    #                     label="API Version",
    #                     value=self.get_settings_for_keys("azure_llm_settings.api_version"),
    #                     on_change=self.on_change("azure_llm_settings.api_version"),
    #                 ),
    #             ]
    #         )
    #     return Column(controls=[Text("Unsupported provider.")])

    # def update_provider_controls(self, e):
    #     """LLMプロバイダーの設定を更新"""
    #     self.llm_provider_column.controls = self.get_provider_specific_controls(e.control.value).controls
    #     self.page.update()

    # def toggle_langsmith_settings_visibility(self, e):
    #     """LangSmith設定の表示・非表示を切り替える"""
    #     self.langsmith_column.visible = e.control.value
    #     self.page.update()

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
        )

        self.controls = [
            self.create_title(save_button_click),
            self.create_tabs(tabs),
        ]

    def create_title(self, save_button_click: callable):
        return Container(
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

    def create_tabs(self, tabs: list[TabView]):
        return Tabs(
            expand=True,
            selected_index=0,
            animation_duration=300,
            tab_alignment=TabAlignment.CENTER,
            tabs=tabs,
        )

    # def save_settings(self, e):
    #     try:
    #         self.settings_manager.save_settings()
    #         self.show_banner(e, "success")
    #     except Exception:
    #         self.show_banner(e, "error")

    # def banner_message(self, status):
    #     """バナーメッセージを表示する"""
    #     self.banner = Banner(
    #         bgcolor="red" if status == "error" else "green",
    #         content=Text("Settings saved successfully!" if status == "success" else "Error saving settings!"),
    #         actions=[IconButton(icon=Icons.CLOSE, on_click=self.close_banner)],
    #     )
    #     return self.banner

    # def close_banner(self, e):
    #     """バナーメッセージを閉じる"""
    #     self.banner.open = False
    #     self.page.update()

    # def show_banner(self, e, status):
    #     """バナーメッセージを表示する"""
    #     self.page.overlay.append(self.banner_message(status))
    #     self.banner.open = True
    #     self.page.update()
    #     time.sleep(3)
    #     self.close_banner(e)
