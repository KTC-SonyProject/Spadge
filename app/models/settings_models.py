from dataclasses import dataclass, field
from enum import Enum


class LlmProvider(Enum):
    AZURE = "azure"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class EmbeddingProvider(Enum):
    AZURE = "azure"


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
class GeminiLlmSettings:
    api_key: str = ""
    model: str = ""


@dataclass
class LangsmithSettings:
    endpoint: str = "https://api.smith.langchain.com"
    project_name: str = ""
    api_key: str = ""


@dataclass
class LlmSettings:
    llm_provider: LlmProvider = LlmProvider.AZURE
    embedding_provider: EmbeddingProvider = EmbeddingProvider.AZURE
    azure_llm_settings: AzureLlmSettings = field(default_factory=AzureLlmSettings)
    gemini_llm_settings: GeminiLlmSettings = field(default_factory=GeminiLlmSettings)
    use_langsmith: bool = False
    langsmith_settings: LangsmithSettings = field(default_factory=LangsmithSettings)

    def get_active_provider_settings(self):
        """現在のプロバイダー設定を取得する"""
        if self.llm_provider == LlmProvider.AZURE:
            return self.azure_llm_settings
        elif self.llm_provider == LlmProvider.GEMINI:
            return self.gemini_llm_settings
        return None


@dataclass
class AppSettings:
    general_settings: GeneralSettings = field(default_factory=GeneralSettings)
    database_settings: DatabaseSettings = field(default_factory=DatabaseSettings)
    llm_settings: LlmSettings = field(default_factory=LlmSettings)


# Enumオブジェクトを文字列に変換するカスタムシリアライザ
def custom_serializer(obj):
    if isinstance(obj, Enum):
        return obj.value  # Enumの値（文字列）を返す
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


DEFAULT_SETTINGS = AppSettings()


if __name__ == "__main__":
    # from app.logging_config import setup_logging
    import json
    from dataclasses import asdict

    # setup_logging()
    print(json.dumps(asdict(DEFAULT_SETTINGS), default=custom_serializer, indent=4))
