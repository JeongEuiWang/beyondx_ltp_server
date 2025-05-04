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
    ) -> UserAddress:
        new_address = UserAddress(
            user_id=user_id,
            name=address_data.name,
            state=address_data.state,
            city=address_data.city,
            county=address_data.county,
            zip_code=address_data.zip_code,
            location_type=address_data.location_type,
            address=address_data.address,
        )
        self.db_session.add(new_address)
        await self.db_session.commit()
        return new_address

    async def get_user_addresses(self, user_id: int) -> List[UserAddress]:
        query = select(UserAddress).where(UserAddress.user_id == user_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()
