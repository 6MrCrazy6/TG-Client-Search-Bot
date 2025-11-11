import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

# === Абсолютный путь к .env ===
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "Keys" / "data_keys.env"
load_dotenv(ENV_PATH)

@dataclass(frozen=True)
class Config:
    """Хранилище всех настроек проекта"""
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DB_URL: str = os.getenv("DATABASE_PUBLIC_URL")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", 0))

    KABANCHIK_LOGIN: str = os.getenv("KABANCHIK_LOGIN")
    KABANCHIK_PASSWORD: str = os.getenv("KABANCHIK_PASSWORD")