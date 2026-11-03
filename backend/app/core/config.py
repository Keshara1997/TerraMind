
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Aleph Next"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    DATABASE_URL: str
    REDIS_URL: str

    API_V1_PREFIX: str = "/api/v1"

    JWT_ACCESS_SECRET: SecretStr
    JWT_REFRESH_SECRET: SecretStr

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
