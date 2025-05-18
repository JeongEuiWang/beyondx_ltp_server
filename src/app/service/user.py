from typing import List

from ..db.unit_of_work import UnitOfWork
from ..schema.user import (
    CreateUserAddressRequest,
    CreateUserAddressResponse,
    GetUserAddressResponse
)
from ..schema.user import (
    CreateUserRequest,
    CreateUserResponse,
    CheckEmailResponse,
    GetUserInfoResponse,
)
from ..core.security import get_password_hash
from ..core.exceptions import BadRequestException, NotFoundException


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def check_email(self, email: str) -> CheckEmailResponse:
        async with self.uow:
            existing_user = await self.uow.users.get_user_by_email(email)
        return CheckEmailResponse(
            is_unique=not existing_user,
        )

    async def create_user(self, user_data: CreateUserRequest) -> CreateUserResponse:
        async with self.uow:
            existing_user = await self.uow.users.get_user_by_email(user_data.email)
        if existing_user:
            raise BadRequestException(message="이미 사용 중인 이메일입니다")
        hashed_password = get_password_hash(user_data.password)
        async with self.uow:
            await self.uow.users.create_user(user_data, hashed_password)
        return CreateUserResponse(success=True)

    async def get_user_info(self, user_id: int) -> GetUserInfoResponse:
        async with self.uow:
            user = await self.uow.users.get_user_by_id(user_id)
            if not user:
                raise NotFoundException(message="사용자를 찾을 수 없습니다")
            user_level = await self.uow.user_levels.get_level_by_id(
                user.user_level_id
            )
            if not user_level:
                raise NotFoundException(message="유효하지 않은 사용자 등급입니다.")
            user_dict = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "total_payment_amount": user.total_payment_amount,
                "user_level": {
                    "id": user_level.id,
                    "level": user_level.user_level,
                    "required_amount": user_level.required_amount,
                    "discount_rate": user_level.discount_rate,
                },
            }
        return GetUserInfoResponse.model_validate(user_dict)

    async def create_user_address(
        self, user_id: int, address_data: CreateUserAddressRequest
    ) -> CreateUserAddressResponse:
        async with self.uow:
            new_address_model = await self.uow.user_addresses.create_user_address(
            user_id, address_data
        )
        return CreateUserAddressResponse.model_validate(new_address_model)

    async def get_user_addresses(self, user_id: int) -> List[GetUserAddressResponse]:
        async with self.uow:
            addresses_models = await self.uow.user_addresses.get_user_addresses_by_id(user_id)
            return [GetUserAddressResponse.model_validate(addr) for addr in addresses_models]
