"""Checks the login token that Supabase gives the browser.

Supabase does the signing up, logging in and password storage. Our backend only has to answer
one question on every request: "is this token really from our Supabase project, and still valid?"
"""

import logging
from functools import lru_cache

import jwt

from app.core.config import get_settings

AUDIENCE = "authenticated"  # Supabase puts this in every logged-in user's token
log = logging.getLogger(__name__)


class InvalidToken(Exception):
    pass


@lru_cache
def _jwks_client(supabase_url: str) -> jwt.PyJWKClient:
    # Supabase publishes its public signing keys here; the client caches them after the first fetch.
    return jwt.PyJWKClient(f"{supabase_url}/auth/v1/.well-known/jwks.json", cache_keys=True)


def verify_token(token: str) -> dict:
    """Return the token's claims (user id in "sub", "email", ...) or raise InvalidToken."""
    settings = get_settings()
    issuer = f"{settings.supabase_url}/auth/v1"
    try:
        # The token's own header says how it was signed. Projects on Supabase's current signing keys use
        # ES256/RS256 (checked with public keys); only legacy projects use HS256 with the shared secret.
        alg = jwt.get_unverified_header(token).get("alg")
        if alg == "HS256":
            if not settings.supabase_jwt_secret:
                raise InvalidToken("HS256 token but SUPABASE_JWT_SECRET is not set")
            key, algorithms = settings.supabase_jwt_secret, ["HS256"]
        else:
            key = _jwks_client(settings.supabase_url).get_signing_key_from_jwt(token).key
            algorithms = ["ES256", "RS256"]
        # decode() also rejects expired tokens and tokens meant for another audience or issuer.
        return jwt.decode(token, key, algorithms=algorithms, audience=AUDIENCE, issuer=issuer)
    except jwt.PyJWTError as e:
        log.warning("Rejected login token: %s", type(e).__name__)  # server log only, never sent to the user
        raise InvalidToken(type(e).__name__) from e
