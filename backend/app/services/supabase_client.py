"""One shared Supabase client for the backend, using the server-only secret key."""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_admin_client() -> Client:
    settings = get_settings()
    if not settings.supabase_secret_key:
        raise RuntimeError("SUPABASE_SECRET_KEY is missing from backend/.env")
    return create_client(settings.supabase_url, settings.supabase_secret_key)
