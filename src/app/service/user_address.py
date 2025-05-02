from fastapi import HTTPException
from ..schema.user_address import (
    CreateUserAddressRequest,
    CreateUserAddressResponse,
    GetUserAddressListResponse,
)
from ..repository.user_address import UserAddressRepository


class UserAddressService:
    def __init__(self, user_address_repository: UserAddressRepository):
        self.user_address_repository = user_address_repository

    async def create_user_address(
        self, user_id: int, address_data: CreateUserAddressRequest
    ) -> CreateUserAddressResponse:
        """
        사용자 주소 생성
        """
        pass

    async def get_user_addresses(self, user_id: int) -> GetUserAddressListResponse:
        """
        사용자 주소 목록 조회
        """
        pass
