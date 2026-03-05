from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Azure / MS Graph
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    mailbox_user_email: str = ""

    # Ollama
    ollama_host: str = "http://ollama:11434"
    ollama_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/support_manager.db"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"

    # App
    dev_mode: bool = False
    sync_interval_minutes: int = 5
    jira_sender: str = "mailer@marbes.cz"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
