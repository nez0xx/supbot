import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent
DOTENV = os.path.join(BASE_DIR, ".env")


class SettingsWithLoadEnvVars(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_file_encoding='utf-8',
        extra='ignore'
    )


class Settings(SettingsWithLoadEnvVars):
    GROUP_ID: int
    GROUP_TYPE: str
    TELEGRAM_TOKEN: str
    WEBHOOK_DOMAIN: str | None = None
    WEBHOOK_PATH: str
    APP_HOST: str
    APP_PORT: int

settings = Settings()
