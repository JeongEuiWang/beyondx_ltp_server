from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from ..model.rate import RateLocation, RateArea, RateAreaCost
from pprint import pprint


class RateRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_rate_location_by_query(
        self, region_id: int, city: Optional[str] = None, zip_code: Optional[str] = None
    ) -> List[RateLocation]:
        query = select(RateLocation).where(RateLocation.region_id == region_id)

        if city is not None and zip_code is not None:
            query = query.where(
                RateLocation.city == city, RateLocation.zip_code == zip_code
            )
        elif city is not None:
            query = query.where(RateLocation.city == city)
        elif zip_code is not None:
            query = query.where(RateLocation.zip_code == zip_code)

        result = await self.db_session.execute(query)
        return result.scalars().all()
      
    async def get_area_by_zip_code(self, zip_code: str) -> Optional[RateArea]:
        query = (
            select(RateArea)
            .join(RateLocation, RateLocation.area_id == RateArea.id)
            .where(RateLocation.zip_code == zip_code)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_area_costs(self, area_id: int) -> List[RateAreaCost]:
        query = select(RateAreaCost).where(RateAreaCost.area_id == area_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()
