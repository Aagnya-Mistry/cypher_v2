"""All settings come from backend/.env (or real environment variables in production), read once."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    supabase_url: str
    supabase_jwt_secret: str = ""  # legacy projects only; empty means verify with Supabase's public keys
    # Server-only key for Storage and the database. Never sent to the browser.
    supabase_secret_key: str = ""
    storage_bucket: str = "documents"
    max_upload_mb: int = 50  # Supabase free plan caps a single stored file at 50 MB
    frontend_origin: str = "http://localhost:5173"
    groq_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
