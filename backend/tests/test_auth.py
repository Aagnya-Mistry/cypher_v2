"""Login-check tests."""

import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.utils import make_token

client = TestClient(app)


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


def test_es256_token_uses_public_keys_even_if_legacy_secret_is_set(monkeypatch):
    """Current Supabase projects sign with ES256. A leftover SUPABASE_JWT_SECRET must not break that."""
    from cryptography.hazmat.primitives.asymmetric import ec

    from app.core import security
    from tests.utils import SUPABASE_URL

    private_key = ec.generate_private_key(ec.SECP256R1())

    class FakeJwks:
        def get_signing_key_from_jwt(self, token):
            return type("Key", (), {"key": private_key.public_key()})()

    monkeypatch.setattr(security, "_jwks_client", lambda url: FakeJwks())
    claims = {
        "sub": "user-es", "email": "es@example.com", "aud": "authenticated",
        "iss": f"{SUPABASE_URL}/auth/v1", "exp": int(time.time()) + 3600,
    }
    import jwt

    token = jwt.encode(claims, private_key, algorithm="ES256")
    r = get_me(token)
    assert r.status_code == 200
    assert r.json()["id"] == "user-es"
