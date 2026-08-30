from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Marketpulse-Scrapper"
    DEBUG: bool = True

    # Database Settings
    DATABASE_URL = r"mssql+pyodbc://.\SQLEXPRESS/SmartInvoiceDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"

    # Telegram Bot Config
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Scrapper Config
    SCRAPE_INTERVAL_MINUTES: int = 30
    HEADLESS_MODE: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()