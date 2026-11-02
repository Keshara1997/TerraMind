
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "TerraMind Next"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    DATABASE_URL: str

    REDIS_URL: str

    API_V1_PREFIX: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached settings instance.
    """
    return Settings()


settings = get_settings()
