"""通过 pydantic-settings 的应用配置。"""

from pathlib import Path

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    DATABASE_URL: str = "sqlite+aiosqlite:///./smarthire.db"

    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    LLM_TIMEOUT_SECONDS: float = Field(default=60.0, gt=0)
    MATCH_CONCURRENCY: int = Field(default=3, ge=1, le=20)
    SEED_ADMIN: bool = False

    APP_NAME: str = "SmartHire"
    DEBUG: bool = False

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024


settings = Settings()

logger.info("Settings loaded from env file and defaults")

_masked_db_url = "****"
if "://" in settings.DATABASE_URL and "@" in settings.DATABASE_URL:
    scheme, rest = settings.DATABASE_URL.split("://", 1)
    userinfo, host = rest.rsplit("@", 1)
    if ":" in userinfo:
        userinfo = userinfo.split(":")[0] + ":****"
    _masked_db_url = f"{scheme}://{userinfo}@{host}"
logger.debug("Key settings: DATABASE_URL={}, DEBUG={}", _masked_db_url, settings.DEBUG)

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
