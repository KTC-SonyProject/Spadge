from dataclasses import dataclass, field


# データクラスで設定の構造を定義
@dataclass
class GeneralSettings:
    app_name: str = "Spadge"
    app_description: str = ""

@dataclass
class PostgresSettings:
    host: str = "postgres"
    port: int = 5432
    database: str = "main_db"
    user: str = "postgres"
    password: str = "postgres"

@dataclass
class SqLiteSettings:
    database: str = "main_db.db"

@dataclass
class DatabaseSettings:
    use_postgres: bool = False
    postgres_settings: PostgresSettings = field(default_factory=PostgresSettings)
    sqlite_settings: SqLiteSettings = field(default_factory=SqLiteSettings)

@dataclass
class AzureLlmSettings:
    endpoint: str = ""
    api_key: str = ""
    deployment_name: str = ""
    deployment_embedding_name: str = ""
    api_version: str = ""

@dataclass
class LangsmithSettings:
    endpoint: str = ""
    project_name: str = ""
    api_key: str = ""

@dataclass
class LlmSettings:
    llm_provider: str = "azure"
    embedding_provider: str = "azure"
    azure_llm_settings: AzureLlmSettings = field(default_factory=AzureLlmSettings)
    use_langsmith: bool = False
    langsmith_settings: LangsmithSettings = field(default_factory=LangsmithSettings)

    def get_active_provider_settings(self):
        """現在のプロバイダー設定を取得する"""
        if self.llm_provider == "azure":
            return self.azure_llm_settings
        return None

@dataclass
class AppSettings:
    general_settings: GeneralSettings = field(default_factory=GeneralSettings)
    database_settings: DatabaseSettings = field(default_factory=DatabaseSettings)
    llm_settings: LlmSettings = field(default_factory=LlmSettings)

DEFAULT_SETTINGS = AppSettings()
