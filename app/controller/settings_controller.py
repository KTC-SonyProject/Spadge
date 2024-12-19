import logging
import time

from flet import (
    Column,
    Divider,
    Page,
    Text,
)

from app.controller.core import AbstractController
from app.controller.settings_manager import SettingsManager
from app.models.settings_models import LlmProvider
from app.views.core import banner_message, create_dropdown, create_switch, create_text_field
from app.views.settings_view import (
    BaseSettingsView,
    SettingsView,
    TabView,
    visible_body_column,
)

logger = logging.getLogger(__name__)

class SettingsController(AbstractController):
    def __init__(self, page: Page, settings_manager: SettingsManager):
        super().__init__(page)
        self.manager = settings_manager

    def _show_banner(self, event, status, message):
        self.banner = banner_message(status, message, self._close_banner)
        self.page.overlay.append(self.banner)
        self.banner.open = True
        self.page.update()
        time.sleep(2)
        self._close_banner(event)

    def _close_banner(self, _):
        self.banner.open = False
        self.page.update()

    def _change_settings_value(self, key: str, update_ui: callable = None):
        def handler(event):
            self.manager.update_setting(key, event.control.value)
            if update_ui:
                update_ui(event)
        return handler

    def _save_settings(self, event):
        try:
            self.manager.save_settings()
            self._show_banner(event, "success", "Settings saved successfully.")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            self._show_banner(event, "error", "Error saving settings.")

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
            ]
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
            ]
        )
        return BaseSettingsView(
            title="Database",
            body_content=[
                create_switch(
                    label="Use Postgres",
                    value=self.manager.get_setting(f"{nested_key}.use_postgres"),
                    on_change=self._change_settings_value(
                        f"{nested_key}.use_postgres",
                        self._toggle_visibility(self.postgres_body)
                    ),
                ),
                self.postgres_body,
            ]
        )

    def _get_provider_body(self, provider: str) -> Column:
        body = []
        if provider == LlmProvider.AZURE.value:
            body = [
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
        elif provider == LlmProvider.GEMINI.value:
            body = [
                Text("Gemini is unsupported provider."),
            ]
        elif provider == LlmProvider.OLLAMA.value:
            body = [
                Text("Ollama is unsupported provider."),
            ]
        return visible_body_column(
            True,
            body
        )

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
            ]
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
                        f"{nested_key}.use_langsmith",
                        self._toggle_visibility(self.langsmith_body)
                    ),
                ),
                self.langsmith_body,
            ]
        )

    def get_view(self) -> SettingsView:
        tabs = [
            TabView("General", self._create_general_tab()),
            TabView("Database", self._create_database_tab()),
            TabView("LLM", self._create_llm_tab()),
        ]
        return SettingsView(tabs, self._save_settings)


if __name__ == "__main__":
    import flet as ft
    def main(page: Page) -> None:
        page.title = "Settings"
        settings_manager = SettingsManager()
        settings_controller = SettingsController(page, settings_manager)
        settings_view = settings_controller.get_view()
        page.add(settings_view)

    ft.app(main)
