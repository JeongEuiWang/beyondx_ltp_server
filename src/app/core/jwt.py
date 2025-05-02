from datetime import UTC, datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt

from .config import settings


def create_access_token(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    주어진 데이터로 JWT 액세스 토큰을 생성합니다.
    """
    to_encode = data.copy()

    # 만료 시간 설정
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # JWT 토큰 생성
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return {"token": encoded_jwt, "expires_at": expire}


def create_refresh_token(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    주어진 데이터로 JWT 리프레시 토큰을 생성합니다.
    """
    to_encode = data.copy()

    # 만료 시간 설정
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})

    # JWT 토큰 생성
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return {"token": encoded_jwt, "expires_at": expire}


def decode_token(token: str) -> Dict[str, Any]:
    """
    JWT 토큰을 디코딩하여 페이로드를 반환합니다.
    디코딩에 실패하면 예외가 발생합니다.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
