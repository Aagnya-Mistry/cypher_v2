"""Shared route requirements. Every private route declares `user: CurrentUser = Depends(get_current_user)`."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import InvalidToken, verify_token

_bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    email: str | None


def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> CurrentUser:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not logged in or session expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if creds is None:
        raise unauthorized
    try:
        claims = verify_token(creds.credentials)
    except InvalidToken:
        raise unauthorized  # same message for every failure: don't tell callers why a token was rejected
    return CurrentUser(id=claims["sub"], email=claims.get("email"))
