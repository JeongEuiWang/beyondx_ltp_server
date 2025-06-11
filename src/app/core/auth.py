from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import Optional

from ..core.exceptions import AuthException
from .jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class TokenData:
    def __init__(self, user_id: int, role_id: int):
        self.user_id = user_id
        self.role_id = role_id


async def get_refresh_token_from_cookie(
    refresh_token: Optional[str] = Cookie(None, alias="ltp_refresh_token")
) -> Optional[str]:
    return refresh_token


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = AuthException(
        message="유효하지 않은 인증 정보입니다.",
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        role_id = payload.get("role_id")

        if user_id is None or role_id is None:
            raise credentials_exception

        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            raise credentials_exception

        return TokenData(user_id=user_id, role_id=role_id)

    except JWTError:
        raise credentials_exception


async def required_authorization(
    token_data: TokenData = Depends(get_current_user),
) -> TokenData:
    return token_data