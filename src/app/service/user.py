from typing import List
from ..db.unit_of_work import UnitOfWork
from ..schema.user import (
    CheckEmailResponse,
    CreateUserRequest,
    CreateUserResponse,
    GetUserInfoResponse,
    CreateUserAddressRequest,
    CreateUserAddressResponse,
    GetUserAddressResponse,
)
from ..core.security import get_password_hash
from ..core.exceptions import (
    BadRequestException,
    NotFoundException,
    ValidationException,
)


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def check_email(self, email: str) -> CheckEmailResponse:
        async with self.uow:
            existing_user = await self.uow.user.get_user_by_email(email)
            if not existing_user:
                raise ValidationException(
                    message="Email already exists", details={"is_unique": False}
                )
            return CheckEmailResponse(
                is_unique=not existing_user,
            )

    async def create_user(self, request: CreateUserRequest) -> CreateUserResponse:
        async with self.uow:
            existing_user = await self.uow.user.get_user_by_email(request.email)
            if existing_user:
                raise BadRequestException(message="Email already exists")
            hashed_password = get_password_hash(request.password)
            await self.uow.user.create_user(request, hashed_password)
            return CreateUserResponse(success=True)

    async def get_user_info(self, user_id: int) -> GetUserInfoResponse:
        async with self.uow:
            user = await self.uow.user.get_user_by_id(user_id)
            if not user:
                raise NotFoundException(message="User not found")

            user_level = await self.uow.user_level.get_level_by_id(user.user_level_id)
            if not user_level:
                raise NotFoundException(message="Invalid user level")

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
        self, user_id: int, request: CreateUserAddressRequest
    ) -> CreateUserAddressResponse:
        async with self.uow:
            user = await self.uow.user.get_user_by_id(user_id)
            if not user:
                raise NotFoundException(message="User not found")

            new_address_model = await self.uow.user_address.create_user_address(
                user_id, request
            )
            return CreateUserAddressResponse.model_validate(new_address_model)

    async def get_user_addresses(self, user_id: int) -> List[GetUserAddressResponse]:
        async with self.uow:
            addresses_models = await self.uow.user_address.get_user_addresses_by_id(
                user_id
            )
            return [
                GetUserAddressResponse.model_validate(addr) for addr in addresses_models
            ]
