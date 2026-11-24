import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHROMA_DIR = DATA_DIR / "chroma"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_PATH = DATA_DIR / "sqlite.db"

class Settings(BaseSettings):
    """Central Application Settings."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "FlowMind AI"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Database
    DATABASE_URL: str = f"sqlite:///{SQLITE_PATH}"
    CHROMA_PERSIST_DIR: str = str(CHROMA_DIR)
    UPLOAD_DIR: str = str(UPLOADS_DIR)

    # Tesseract path override if needed on Windows
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")

settings = Settings()
