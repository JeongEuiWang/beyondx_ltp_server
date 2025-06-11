from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.model.cargo import CargoTransportation, CargoAccessorial, CargoPackage


class CargoRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_cargo_transportation(
        self,
    ) -> List[CargoTransportation]:
        query = select(CargoTransportation)
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
    async def get_cargo_accessorial(
        self,
    ) -> List[CargoAccessorial]:
        query = select(CargoAccessorial)
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
    async def get_cargo_package(
        self,
    ) -> List[CargoPackage]:
        query = select(CargoPackage)
        result = await self.db_session.execute(query)
        return result.scalars().all()
