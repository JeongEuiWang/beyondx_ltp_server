from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..model.user import UserAddress
from ..schema.user import CreateUserAddressRequest


class UserAddressRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user_address(
        self, user_id: int, request: CreateUserAddressRequest
    ) -> UserAddress:
        new_address = UserAddress(
            name=request.name,
            state=request.state,
            county=request.county,
            city=request.city,
            zip_code=request.zip_code,
            location_type=request.location_type,
            address=request.address,
            user_id=user_id
        )
        self.db_session.add(new_address)
        await self.db_session.flush()
        return new_address

    async def get_user_addresses_by_id(self, user_id: int) -> List[UserAddress]:
        query = select(UserAddress).where(UserAddress.user_id == user_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()
