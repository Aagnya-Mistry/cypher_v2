"""All settings come from backend/.env (or real environment variables in production), read once."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    supabase_url: str
    supabase_jwt_secret: str = ""  # legacy projects only; empty means verify with Supabase's public keys
    frontend_origin: str = "http://localhost:5173"
    groq_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
