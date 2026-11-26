"""Login-check tests. They use the legacy shared-secret mode so no real Supabase project is needed."""

import os
import time

import jwt
import pytest

SUPABASE_URL = "https://test-project.supabase.co"
SECRET = "test-secret-at-least-32-characters-long!!"

os.environ.update(SUPABASE_URL=SUPABASE_URL, SUPABASE_JWT_SECRET=SECRET)

from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()
from app.main import app  # noqa: E402

client = TestClient(app)


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


def get_me(token: str | None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.get("/api/auth/me", headers=headers)


def test_health_is_public():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_valid_token_returns_user():
    r = get_me(make_token())
    assert r.status_code == 200
    assert r.json() == {"id": "user-123", "email": "analyst@example.com"}


@pytest.mark.parametrize(
    "token",
    [
        None,                                              # not logged in
        "not-a-jwt",                                       # garbage
        make_token(exp=int(time.time()) - 10),             # expired
        make_token(_secret="someone-elses-secret-32-chars-long!!"),  # forged signature
        make_token(aud="anon"),                            # not a logged-in user's token
        make_token(iss="https://other-project.supabase.co/auth/v1"),  # another Supabase project
    ],
)
def test_bad_tokens_are_rejected(token):
    r = get_me(token)
    assert r.status_code == 401
    assert r.json()["detail"] == "Not logged in or session expired"


def test_cors_allows_only_frontend():
    ok = client.options("/api/auth/me", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    bad = client.options("/api/auth/me", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in bad.headers
