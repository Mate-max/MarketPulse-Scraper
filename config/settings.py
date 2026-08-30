from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "MarketPulse-Scraper"
    DEBUG: bool = True

    # Database Settings (შენი ლოკალური MSSQL)
    DATABASE_URL: str = (
        r"mssql+pyodbc://.\SQLEXPRESS/SmartInvoiceDB?"
        r"driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
    )

    # Telegram Bot Config
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Scraper Config
    SCRAPE_INTERVAL_MINUTES: int = 30
    HEADLESS_MODE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()