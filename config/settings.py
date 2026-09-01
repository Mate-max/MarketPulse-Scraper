from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()  # .env ფაილის ჩატვირთვა

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "MarketPulse-Scraper"
    DEBUG: bool = True

    # Database Settings (შენი ლოკალური MSSQL)
    DATABASE_URL:str = os.getenv("DATABASE_URL")

    # Telegram Bot Config
    TELEGRAM_BOT_TOKEN:str = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID:str = os.getenv("TELEGRAM_CHAT_ID")

    # Scraper Config
    SCRAPE_INTERVAL_MINUTES: int = 30
    HEADLESS_MODE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()