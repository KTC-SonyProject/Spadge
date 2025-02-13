import logging

from flet import (
    Column,
    Divider,
    ElevatedButton,
    Page,
    Text,
)

from app.controller.core import AbstractController
from app.controller.manager.auth_manager import AuthManager
from app.controller.manager.settings_manager import SettingsManager
from app.models.settings_models import LlmProvider
from app.views.core import BannerView, create_dropdown, create_switch, create_text_field
from app.views.settings_view import (
    BaseSettingsView,
    SettingsView,
    TabView,
    visible_body_column,
)

logger = logging.getLogger(__name__)


class SettingsController(AbstractController):
    def __init__(self, page: Page, settings_manager: SettingsManager, auth_manager: AuthManager):
        super().__init__(page)
        self.manager = settings_manager
        self.auth_manager = auth_manager
        self.banner = BannerView(page)

    def _change_settings_value(self, key: str, update_ui: callable = None):
        def handler(event):
            self.manager.update_setting(key, event.control.value)
            if update_ui:
                update_ui(event)

        return handler

    def _save_settings(self, event):
        try:
            self.manager.save_settings()
            self.banner.show_banner("success", "Settings saved successfully.")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            self.banner.show_banner("error", "Error saving settings.")

    def _toggle_visibility(self, visible_body: Column):
        def update_ui(event):
            visible_body.visible = event.control.value
            self.page.update()

        return update_ui

    def _create_general_tab(self) -> BaseSettingsView:
        nested_key = "general_settings"
        return BaseSettingsView(
            title="General",
            body_content=[
                create_text_field(
                    label="App Name",
                    value=self.manager.get_setting(f"{nested_key}.app_name"),
                    on_change=self._change_settings_value("name"),
                ),
                create_text_field(
                    label="App Description",
                    value=self.manager.get_setting(f"{nested_key}.app_description"),
                    on_change=self._change_settings_value("app_description"),
                ),
                ElevatedButton(
                    text="認証アカウントのIDとパスワードを変更する",
                    on_click=lambda _: self.page.go("/settings/auth/update"),
                ),
            ],
        )

    def _create_database_tab(self) -> BaseSettingsView:
        nested_key = "database_settings"
        self.postgres_body = visible_body_column(
            self.manager.get_setting(f"{nested_key}.use_postgres"),
            [
                create_text_field(
                    label="Host",
                    value=self.manager.get_setting(f"{nested_key}.postgres_settings.host"),
                    on_change=self._change_settings_value(f"{nested_key}.postgres_settings.host"),
                ),
                create_text_field(
                    label="Port",
                    value=self.manager.get_setting(f"{nested_key}.postgres_settings.port"),
                    on_change=self._change_settings_value(f"{nested_key}.postgres_settings.port"),
                ),
                create_text_field(
                    label="User",
                    value=self.manager.get_setting(f"{nested_key}.postgres_settings.user"),
                    on_change=self._change_settings_value(f"{nested_key}.postgres_settings.user"),
                ),
                create_text_field(
                    label="Password",
                    value=self.manager.get_setting(f"{nested_key}.postgres_settings.password"),
                    on_change=self._change_settings_value(f"{nested_key}.postgres_settings.password"),
                    password=True,
                    can_reveal_password=True,
                ),
                create_text_field(
                    label="Database",
                    value=self.manager.get_setting(f"{nested_key}.postgres_settings.database"),
                    on_change=self._change_settings_value(f"{nested_key}.postgres_settings.database"),
                ),
            ],
        )
        return BaseSettingsView(
            title="Database",
            body_content=[
                create_switch(
                    label="Use Postgres",
                    value=self.manager.get_setting(f"{nested_key}.use_postgres"),
                    on_change=self._change_settings_value(
                        f"{nested_key}.use_postgres", self._toggle_visibility(self.postgres_body)
                    ),
                ),
                self.postgres_body,
            ],
        )

    def _get_azure_provider_body(self) -> Column:
        return [
            create_text_field(
                label="Endpoint",
                value=self.manager.get_setting("llm_settings.azure_llm_settings.endpoint"),
                on_change=self._change_settings_value("llm_settings.azure_llm_settings.endpoint"),
            ),
            create_text_field(
                label="API Key",
                value=self.manager.get_setting("llm_settings.azure_llm_settings.api_key"),
                on_change=self._change_settings_value("llm_settings.azure_llm_settings.api_key"),
            ),
            create_text_field(
                label="Deployment Name",
                value=self.manager.get_setting("llm_settings.azure_llm_settings.deployment_name"),
                on_change=self._change_settings_value("llm_settings.azure_llm_settings.deployment_name"),
            ),
            create_text_field(
                label="Deployment Embedding Name",
                value=self.manager.get_setting("llm_settings.azure_llm_settings.deployment_embedding_name"),
                on_change=self._change_settings_value("llm_settings.azure_llm_settings.deployment_embedding_name"),
            ),
            create_text_field(
                label="API Version",
                value=self.manager.get_setting("llm_settings.azure_llm_settings.api_version"),
                on_change=self._change_settings_value("llm_settings.azure_llm_settings.api_version"),
            ),
        ]

    def _get_gemini_provider_body(self) -> Column:
        return [
            create_text_field(
                label="API Key",
                value=self.manager.get_setting("llm_settings.gemini_llm_settings.api_key"),
                on_change=self._change_settings_value("llm_settings.gemini_llm_settings.api_key"),
            ),
            create_text_field(
                label="Model",
                value=self.manager.get_setting("llm_settings.gemini_llm_settings.model"),
                on_change=self._change_settings_value("llm_settings.gemini_llm_settings.model"),
            ),
        ]

    def _get_provider_body(self, provider: str) -> Column:
        body = []
        if provider == LlmProvider.AZURE.value:
            body = self._get_azure_provider_body()
        elif provider == LlmProvider.GEMINI.value:
            body = self._get_gemini_provider_body()
        elif provider == LlmProvider.OLLAMA.value:
            body = [
                Text("Ollama is unsupported provider."),
            ]
        else:
            body = [Text("Unknown provider selected.")]
        return visible_body_column(True, body)

    def _update_provider_body(self, event):
        provider = event.control.value
        self.llm_provider_body.controls = self._get_provider_body(provider).controls
        self.page.update()

    def _create_llm_tab(self) -> BaseSettingsView:
        nested_key = "llm_settings"
        self.llm_provider_body = self._get_provider_body(self.manager.get_setting(f"{nested_key}.llm_provider"))
        self.langsmith_body = visible_body_column(
            self.manager.get_setting(f"{nested_key}.use_langsmith"),
            [
                create_text_field(
                    label="Project Name",
                    value=self.manager.get_setting(f"{nested_key}.langsmith_settings.project_name"),
                    on_change=self._change_settings_value(f"{nested_key}.langsmith_settings.project_name"),
                ),
                create_text_field(
                    label="API Key",
                    value=self.manager.get_setting(f"{nested_key}.langsmith_settings.api_key"),
                    on_change=self._change_settings_value(f"{nested_key}.langsmith_settings.api_key"),
                    password=True,
                    can_reveal_password=True,
                ),
            ],
        )
        return BaseSettingsView(
            title="LLM Provider",
            body_content=[
                create_dropdown(
                    label="LLM Provider",
                    value=self.manager.get_setting(f"{nested_key}.llm_provider"),
                    items=[provider.value for provider in LlmProvider],
                    on_change=self._change_settings_value(f"{nested_key}.llm_provider", self._update_provider_body),
                ),
                self.llm_provider_body,
                Divider(),
                create_switch(
                    label="Use Langsmith",
                    value=self.manager.get_setting(f"{nested_key}.use_langsmith"),
                    on_change=self._change_settings_value(
                        f"{nested_key}.use_langsmith", self._toggle_visibility(self.langsmith_body)
                    ),
                ),
                self.langsmith_body,
            ],
        )

    def get_view(self) -> SettingsView:
        # Check if user is authenticated
        if not self.auth_manager.check_is_authenticated():
            # self.banner.show_banner("error", "You need to login first.")
            self.page.go("/login/error")
            return

        tabs = [
            TabView("General", self._create_general_tab()),
            TabView("Database", self._create_database_tab()),
            TabView("LLM", self._create_llm_tab()),
        ]
        return SettingsView(tabs, self._save_settings)


if __name__ == "__main__":
    from flet import app

    def main(page: Page) -> None:
        page.title = "Settings"
        settings_manager = SettingsManager()
        settings_controller = SettingsController(page, settings_manager)
        settings_view = settings_controller.get_view()
        page.add(settings_view)

    app(main)
