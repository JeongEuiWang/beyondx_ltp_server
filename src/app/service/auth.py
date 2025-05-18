from datetime import UTC, datetime
from fastapi import Response

from ..schema.auth import LoginRequest, LoginResponse, RefreshTokenResponse

from ..core.security import verify_password
from ..core.jwt import create_access_token, create_refresh_token

from ..db.unit_of_work import UnitOfWork
from ..core.exceptions import AuthException, NotFoundException
from ..core.config import settings


class AuthService:
    def __init__(
        self,
        uow: UnitOfWork,  # UoW 주입
    ):
        self.uow = uow

    async def login(self, request: LoginRequest, response: Response) -> LoginResponse:
        async with self.uow:  # UoW 컨텍스트 사용
            user = await self.uow.users.get_user_by_email(request.email)
        if not user:
            raise AuthException(message="사용자를 찾을 수 없습니다.")

        if not verify_password(request.password, user.password):
            raise AuthException(message="비밀번호가 일치하지 않습니다.")

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

        user_level = await self.uow.user_levels.get_level_by_id(user.user_level_id)

        if not user_level:
            raise NotFoundException(message="유효하지 않은 사용자 레벨입니다.")

        user_dict = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "total_payment_amount": user.total_payment_amount,
            "access": access,
            "user_level": {
                "id": user_level.id,
                "level": user_level.user_level,
                "required_amount": user_level.required_amount,
                "discount_rate": user_level.discount_rate,
            },
        }

        return LoginResponse.model_validate(user_dict)

    async def refresh_token(
        self, user_id: int, role_id: int, response: Response
    ) -> RefreshTokenResponse:
        async with self.uow:  # UoW 컨텍스트 사용
            user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다.")

        # 새 토큰 생성
        new_token_data = {"sub": str(user_id), "role_id": role_id}
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

        user_level = await self.uow.user_levels.get_level_by_id(user.user_level_id)

        if not user_level:
            raise NotFoundException(message="유효하지 않은 사용자 레벨입니다.")

        user_dict = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "total_payment_amount": user.total_payment_amount,
            "access": access,
            "user_level": {
                "id": user_level.id,
                "level": user_level.user_level,
                "required_amount": user_level.required_amount,
                "discount_rate": user_level.discount_rate,
            },
        }

        return RefreshTokenResponse.model_validate(user_dict)
