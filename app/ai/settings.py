import logging
import os
from typing import Any

from langchain.globals import set_verbose
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from app.controller.settings_manager import load_settings
from app.models.settings_models import EmbeddingProvider, LlmProvider

logger = logging.getLogger(__name__)


def llm_settings(verbose: bool = False) -> Any:
    set_verbose(verbose)
    settings = load_settings("llm_settings")
    if settings.get("llm_provider") == LlmProvider.AZURE.value:
        settings = settings.get("azure_llm_settings")
        # 変数が空文字の場合はエラーを出す
        for key in settings:
            if settings[key] == "":
                raise ValueError(f"Invalid setting: {key}")
        os.environ["AZURE_OPENAI_ENDPOINT"] = settings.get("endpoint")
        os.environ["AZURE_OPENAI_API_KEY"] = settings.get("api_key")
        return AzureChatOpenAI(
            deployment_name=settings.get("deployment_name"),
            api_version=settings.get("api_version"),
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            streaming=True,
        )
    elif settings.get("llm_provider") == LlmProvider.GEMINI.value:
        print("Gemini is not implemented yet.")
        raise ValueError(f"Invalid LLM type: {settings.get("llm_provider")}")
    elif settings.get("llm_provider") == LlmProvider.OLLAMA.value:
        print("Ollama is not implemented yet.")
        raise ValueError(f"Invalid LLM type: {settings.get("llm_provider")}")
    else:
        raise ValueError(f"Invalid LLM type: {settings.get("llm_provider")}")


def embedding_model_settings():
    settings = load_settings("llm_settings")
    if settings.get("embedding_provider") == EmbeddingProvider.AZURE.value:
        settings = settings.get("azure_llm_settings")
        os.environ["AZURE_OPENAI_API_KEY"] = settings.get("api_key")
        model_name: str = settings.get("deployment_embedding_name")
        return AzureOpenAIEmbeddings(
            model=model_name,
            azure_endpoint=settings.get("endpoint"),
            openai_api_version=settings.get("api_version"),
        )
    else:
        raise ValueError(f"Invalid embedding model type: {settings.get("embedding_provider")}")


def langsmith_settigns():
    settings = load_settings("llm_settings")
    if settings.get("use_langsmith"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = settings["langsmith_settings"].get("endpoint")
        os.environ["LANGCHAIN_PROJECT"] = settings["langsmith_settings"].get("project_name", "spadge-project")
        os.environ["LANGCHAIN_API_KEY"] = settings["langsmith_settings"].get("api_key")
        logger.info("Langsmith is setting.")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        logger.info("Langsmith is not setting.")


if __name__ == "__main__":
    llm = llm_settings(verbose=True)
    print(llm.invoke("こんにちは、世界！"))
