from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ..model.rate import RateLocation


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
