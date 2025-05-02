from typing import Optional, Dict, Any
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status, Response

from ..schema.auth import LoginRequest, LoginResponse, RefreshTokenResponse
from ..core.auth import TokenData
from ..core.security import verify_password, get_password_hash
from ..core.jwt import create_access_token, create_refresh_token
from ..repository.user import UserRepository
from ..core.config import settings


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def login(self, request: LoginRequest, response: Response) -> LoginResponse:
        user = await self.user_repository.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Found"
            )

        if not verify_password(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
            )

        # 토큰 생성
        token_data = {"sub": str(user.id), "role_id": user.role_id}
        access = create_access_token(data=token_data)
        refresh = create_refresh_token(data=token_data)

        # Refresh 토큰을 쿠키에 설정
        expires = datetime.fromtimestamp(refresh["expires_at"].timestamp(), tz=UTC)
        response.set_cookie(
            key="ltp_refresh_token",
            value=refresh["token"],
            httponly=True,
            secure=settings.COOKIE_SECURE,  # HTTPS에서만 전송
            samesite="lax",
            expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            max_age=int((expires - datetime.now(UTC)).total_seconds()),
        )

        return LoginResponse(
            id=user.id,
            email=user.email,
            role_id=user.role_id,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            total_payment_amount=user.total_payment_amount,
            user_level_id=user.user_level_id,
            access=access,
        )

    async def refresh_token(
        self, token_data: TokenData, response: Response
    ) -> RefreshTokenResponse:
        user = await self.user_repository.get_user_by_id(token_data.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # 새 토큰 생성
        new_token_data = {"sub": str(user.id), "role_id": user.role_id}
        access = create_access_token(data=new_token_data)
        refresh = create_refresh_token(data=new_token_data)

        # 새 Refresh 토큰을 쿠키에 설정
        expires = datetime.fromtimestamp(refresh["expires_at"].timestamp(), tz=UTC)
        response.set_cookie(
            key="ltp_refresh_token",
            value=refresh["token"],
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            max_age=int((expires - datetime.now(UTC)).total_seconds()),
        )

        return RefreshTokenResponse(
            id=user.id,
            email=user.email,
            role_id=user.role_id,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            total_payment_amount=user.total_payment_amount,
            user_level_id=user.user_level_id,
            access=access,
        )
