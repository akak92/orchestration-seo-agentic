from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://newsroom:changeme@postgres:5432/newsroom_db"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    # JWT
    JWT_SECRET_KEY: str = "insecure-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Agent service
    AGENT_SERVICE_URL: str = "http://agent:8001"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Token interno para comunicación entre servicios
    INTERNAL_TOKEN: str = "insecure-internal-token-change-in-production"

    # General
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"


settings = Settings()
