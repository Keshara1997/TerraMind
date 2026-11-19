
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT = _BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            _BACKEND_ROOT / ".env",
            _REPO_ROOT / ".env",
        ),
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "TERRAMIND"
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

    CELERY_TASK_DEFAULT_QUEUE: str = "aleph-captures"
    CAPTURE_MAX_FEATURES: int = 1000

    STAC_API_URL: str = "https://earth-search.aws.element84.com/v1"
    STAC_COLLECTION: str = "sentinel-2-l2a"
    STAC_REQUEST_TIMEOUT: int = 45
    STAC_MAX_ITEMS: int = 20

    DATASET_STORAGE_DIR: str = "/data/terra-mind/datasets"
    S3_BUCKET_NAME: str | None = None
    AWS_REGION: str = "ap-south-1"
    NDVI_NODATA: float = -9999.0
    NDVI_MIN_VALID_PIXELS: int = 10

    TITILER_INTERNAL_URL: str = "http://titiler:8000"


    AI_ENABLED: bool = False
    AI_PROVIDER: str = "openai"
    AI_MODEL: str = "gpt-5"
    AI_API_KEY: str | None = None
    AI_BASE_URL: str | None = None
    AI_REQUEST_TIMEOUT: int = 60
    AI_MAX_OUTPUT_TOKENS: int = 1500
    AI_TEMPERATURE: float = 0.2

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
