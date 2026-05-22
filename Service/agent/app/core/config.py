from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Azure OpenAI
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-5.3-chat"
    AZURE_OPENAI_VERSION: str = "2024-12-01-preview"

    # PostgreSQL (para herramientas de memoria y checkpointer)
    DATABASE_URL: str = "postgresql+asyncpg://newsroom:changeme@postgres:5432/newsroom_db"
    # asyncpg necesita URL sin +asyncpg para conexión directa
    DATABASE_URL_SYNC: str = "postgresql://newsroom:changeme@postgres:5432/newsroom_db"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Token interno para comunicación entre servicios
    INTERNAL_TOKEN: str = "insecure-internal-token-change-in-production"

    LOG_LEVEL: str = "INFO"


settings = Settings()
