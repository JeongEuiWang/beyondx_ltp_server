from typing import List

from ..repository.user_address import UserAddressRepository
from ..repository.user_level import UserLevelRepository
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
from ..repository.user import UserRepository


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_level_repository: UserLevelRepository,
        user_address_repository: UserAddressRepository,
    ):
        self.user_repository = user_repository
        self.user_level_repository = user_level_repository
        self.user_address_repository = user_address_repository

    async def check_email(self, email: str) -> CheckEmailResponse:
        existing_user = await self.user_repository.get_user_by_email(email)
        return CheckEmailResponse(
            is_unique=not existing_user,
        )

    async def create_user(self, user_data: CreateUserRequest) -> CreateUserResponse:
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise BadRequestException(message="이미 사용 중인 이메일입니다")
        hashed_password = get_password_hash(user_data.password)
        await self.user_repository.create_user(user_data, hashed_password)
        return CreateUserResponse(success=True)

    async def get_user_info(self, user_id: int) -> GetUserInfoResponse:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다")
        user_level = await self.user_level_repository.get_level_by_id(
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
        new_address = await self.user_address_repository.create_user_address(
            user_id, address_data
        )
        return CreateUserAddressResponse.model_validate(new_address)

    async def get_user_addresses(self, user_id: int) -> List[GetUserAddressResponse]:
        addresses = await self.user_address_repository.get_user_addresses_by_id(user_id)
        return [GetUserAddressResponse.model_validate(addr) for addr in addresses]
