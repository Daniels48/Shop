import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class DatabaseConfig:
    def __init__(self):
        self.dbname = os.getenv("DB_NAME", "shop_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST", "127.0.0.1")
        self.port = int(os.getenv("DB_PORT", "5432"))

        if not self.password:
            raise ValueError("Не задан DB_PASSWORD в файле .env")


db_config = DatabaseConfig()


global_path_resorces = "view/resources"
global_path_icons = f"{global_path_resorces}/icons"
global_path_audio = f"{global_path_resorces}/audio"