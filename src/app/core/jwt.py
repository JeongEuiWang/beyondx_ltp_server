from datetime import UTC, datetime, timedelta
from typing import Dict, Any, Literal
from jose import jwt
from .config import settings


def _create_token(
    data: Dict[str, Any], token_type: Literal["access", "refresh"]
) -> Dict[str, Any]:
    to_encode = data.copy()

    if token_type == "access":
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    else:  # refresh
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return {"token": encoded_jwt, "expires_at": expire}


def create_access_token(data: Dict[str, Any]) -> Dict[str, Any]:
    return _create_token(data, "access")


def create_refresh_token(data: Dict[str, Any]) -> Dict[str, Any]:
    return _create_token(data, "refresh")


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
