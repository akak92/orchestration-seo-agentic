from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    API_SERVICE_URL: str = "http://api:8000"
    INTERNAL_TOKEN: str = "insecure-internal-token-change-in-production"
    LOG_LEVEL: str = "INFO"


settings = Settings()
