from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..model.user import UserAddress
from ..schema.user_address import CreateUserAddressRequest


class UserAddressRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user_address(
        self, user_id: int, address_data: CreateUserAddressRequest
    ):
        """
        사용자 주소 생성
        """
        pass

    async def get_user_addresses(self, user_id: int) -> List[UserAddress]:
        """
        사용자 주소 목록 조회
        """
        pass
