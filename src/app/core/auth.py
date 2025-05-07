from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import Optional

from ..core.exceptions import AuthException
from .jwt import decode_token

# 토큰 URL 설정 (로그인 엔드포인트)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class TokenData:
    def __init__(self, user_id: int, role_id: int):
        self.user_id = user_id
        self.role_id = role_id


# 쿠키에서 refresh token 읽기
async def get_refresh_token_from_cookie(
    refresh_token: Optional[str] = Cookie(None, alias="ltp_refresh_token")
) -> Optional[str]:
    return refresh_token


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    현재 요청의 토큰을 검증하고 유저 정보를 반환합니다.
    """
    credentials_exception = AuthException(
        message="유효하지 않은 인증 정보입니다.",
    )

    try:
        # 토큰 디코딩
        payload = decode_token(token)

        # 유저 ID와 사용자명 추출
        user_id = payload.get("sub")
        role_id = payload.get("role_id")

        if user_id is None or role_id is None:
            raise credentials_exception

        # 숫자 형태의 user_id로 변환
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            raise credentials_exception

        # 토큰 데이터 반환
        return TokenData(user_id=user_id, role_id=role_id)

    except JWTError:
        raise credentials_exception


# 인증을 필요로 하는 API 엔드포인트에서 사용할 의존성 함수
async def required_authorization(
    token_data: TokenData = Depends(get_current_user),
) -> TokenData:
    return token_data