from fastapi import HTTPException
from ..schema.user_address import (
    CreateUserAddressRequest,
    CreateUserAddressResponse,
    UserAddressResponse,
)
from ..repository.user_address import UserAddressRepository
from typing import List


class UserAddressService:
    def __init__(self, user_address_repository: UserAddressRepository):
        self.user_address_repository = user_address_repository

    async def create_user_address(
        self, user_id: int, address_data: CreateUserAddressRequest
    ) -> CreateUserAddressResponse:
        return await self.user_address_repository.create_user_address(
            user_id, address_data
        )

    async def get_user_addresses(self, user_id: int) -> List[UserAddressResponse]:
        addresses = await self.user_address_repository.get_user_addresses(user_id)
        return [UserAddressResponse.model_validate(addr) for addr in addresses]
