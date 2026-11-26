"""Shared test helpers. Tests use the legacy shared-secret mode, so no real Supabase project is needed."""

import time

import jwt

SUPABASE_URL = "https://test-project.supabase.co"
SECRET = "test-secret-at-least-32-characters-long!!"


def make_token(**overrides) -> str:
    claims = {
        "sub": "user-123",
        "email": "analyst@example.com",
        "aud": "authenticated",
        "iss": f"{SUPABASE_URL}/auth/v1",
        "exp": int(time.time()) + 3600,
    }
    claims.update(overrides)
    secret = claims.pop("_secret", SECRET)
    return jwt.encode(claims, secret, algorithm="HS256")


def auth_header(**overrides) -> dict:
    return {"Authorization": f"Bearer {make_token(**overrides)}"}
