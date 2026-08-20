"""
Centralized application configuration.

All settings are read from environment variables (populated via .env in local
dev, or real environment variables in deployed environments). Nothing here
should ever be hard-coded — this is the one place secrets/config are allowed
to be referenced from.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"

    database_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Single shared settings instance, imported wherever config is needed.
settings = Settings()
