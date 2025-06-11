from datetime import UTC, datetime, timedelta
from fastapi import Response

from ..schema.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenResponse,
    LogoutResponse,
)
from ..model.user import User
from ..model.user import UserLevel

from ..core.security import verify_password
from ..core.jwt import create_access_token, create_refresh_token

from ..db.unit_of_work import UnitOfWork
from ..core.exceptions import AuthException, NotFoundException
from ..core.config import settings


class AuthService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    def _set_refresh_token_cookie(self, response: Response, refresh_token_info: dict):
        expires_timestamp = refresh_token_info["expires_at"]
        if isinstance(expires_timestamp, (int, float)):
            expires_dt = datetime.fromtimestamp(expires_timestamp, tz=UTC)
        elif isinstance(expires_timestamp, datetime):
            expires_dt = expires_timestamp
        else:
            expires_dt = datetime.now(UTC) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        response.set_cookie(
            key="ltp_refresh_token",
            value=refresh_token_info["token"],
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            expires=expires_dt.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            max_age=int((expires_dt - datetime.now(UTC)).total_seconds()),
        )

    def _clear_refresh_token_cookie(self, response: Response):
        response.delete_cookie(
            key="ltp_refresh_token",
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
        )

    def _prepare_auth_user_data(
        self, user: User, user_level: UserLevel, access_token_info: dict
    ) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "total_payment_amount": user.total_payment_amount,
            "access": access_token_info,
            "role_id": user.role_id,
            "user_level": {
                "id": user_level.id,
                "level": user_level.user_level,
                "required_amount": user_level.required_amount,
                "discount_rate": user_level.discount_rate,
            },
        }

    async def login(self, request: LoginRequest, response: Response) -> LoginResponse:
        async with self.uow:
            user = await self.uow.user.get_user_by_email(request.email)
            if not user:
                raise AuthException(message="사용자를 찾을 수 없습니다.")

            if not verify_password(request.password, user.password):
                raise AuthException(message="비밀번호가 일치하지 않습니다.")

            token_data = {"sub": str(user.id), "role_id": user.role_id}
            access_token_info = create_access_token(data=token_data)
            refresh_token_info = create_refresh_token(data=token_data)

            self._set_refresh_token_cookie(response, refresh_token_info)

        async with self.uow:
            user_level = await self.uow.user_level.get_level_by_id(user.user_level_id)
            if not user_level:
                raise NotFoundException(message="유효하지 않은 사용자 레벨입니다.")

            user_data_dict = self._prepare_auth_user_data(
                user, user_level, access_token_info
            )
            return LoginResponse.model_validate(user_data_dict)

    async def refresh_token(
        self, user_id: int, role_id: int, response: Response
    ) -> RefreshTokenResponse:
        async with self.uow:
            user = await self.uow.user.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다.")

        new_token_data = {"sub": str(user_id), "role_id": role_id}
        new_access_token_info = create_access_token(data=new_token_data)
        new_refresh_token_info = create_refresh_token(data=new_token_data)

        self._set_refresh_token_cookie(response, new_refresh_token_info)

        async with self.uow:
            user_level = await self.uow.user_level.get_level_by_id(user.user_level_id)
        if not user_level:
            raise NotFoundException(message="유효하지 않은 사용자 레벨입니다.")

        user_data_dict = self._prepare_auth_user_data(
            user, user_level, new_access_token_info
        )
        return RefreshTokenResponse.model_validate(user_data_dict)

    async def logout(self, response: Response) -> LogoutResponse:
        async with self.uow:
            self._clear_refresh_token_cookie(response)
            return LogoutResponse(success=True, message="Successfully logged out")
