from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Annotated, Optional, Dict, Any

from .jwt import decode_token
from app.model.user import Role
from app.model._enum import RoleEnum
from app.db.session import get_async_session

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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
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
    """
    인증이 필요한 엔드포인트에서 사용할 의존성 함수입니다.
    """
    return token_data


# # 인증이 선택적인 API 엔드포인트에서 사용할 의존성 함수
# async def optional_authorization(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[TokenData]:
#     """
#     인증이 선택적인 엔드포인트에서 사용할 의존성 함수입니다.
#     토큰이 유효하지 않으면 None을 반환합니다.
#     """
#     if token is None:
#         return None

#     try:
#         # 토큰 디코딩
#         payload = decode_token(token)

#         # 유저 ID와 사용자명 추출
#         user_id = payload.get("sub")
#         role_id = payload.get("role_id")

#         if user_id is None or role_id is None:
#             return None

#         # 숫자 형태의 user_id로 변환
#         try:
#             user_id = int(user_id)
#         except (ValueError, TypeError):
#             return None

#         # 토큰 데이터 반환
#         return TokenData(user_id=user_id, role_id=role_id)

#     except JWTError:
#         return None

# async def admin_required(
#     token_data: TokenData = Depends(get_current_user),
#     db: AsyncSession = Depends(get_async_session)
# ) -> TokenData:
#     """
#     ADMIN 권한을 가진 사용자만 접근을 허용하는 미들웨어
#     """
#     # DB에서 Role 정보 조회
#     stmt = select(Role).where(Role.id == token_data.role_id)
#     result = await db.execute(stmt)
#     role = result.scalar_one_or_none()

#     # 역할이 존재하지 않거나 ADMIN이 아닌 경우
#     if not role or role.role != RoleEnum.ADMIN:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="관리자 권한이 필요합니다"
#         )

#     return token_data

requiredAuthDeps = Annotated[TokenData, Depends(required_authorization)]
cookieAuthDeps = Annotated[Optional[str], Depends(get_refresh_token_from_cookie)]
