from fastapi import HTTPException

from ..schema.user import (
    CreateUserRequest,
    CreateUserResponse,
    CheckEmailResponse,
    GetUserInfoResponse,
)
from ..core.security import get_password_hash
from ..repository.user import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def check_email(self, email: str) -> CheckEmailResponse:
        existing_user = await self.user_repository.get_user_by_email(email)

        return CheckEmailResponse(
            is_unique=not existing_user,
        )

    async def create_user(self, user_data: CreateUserRequest) -> CreateUserResponse:

        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")

        hashed_password = get_password_hash(user_data.password)

        await self.user_repository.create_user(user_data, hashed_password)

        return CreateUserResponse(success=True)

    async def get_user_info(self, user_id: int) -> GetUserInfoResponse:
        user = await self.user_repository.get_user_by_id(user_id)
        print(user)
        return GetUserInfoResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            total_payment_amount=user.total_payment_amount,
            user_level_id=user.user_level_id,
        )
