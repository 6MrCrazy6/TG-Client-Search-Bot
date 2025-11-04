import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv('Keys/data_keys.env')

@dataclass(frozen=True)
class Config:
    """Хранилище всех настроек проекта"""
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DB_URL: str = os.getenv("DB_URL")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", 0))
