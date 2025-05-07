from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from ..model.rate import RateArea, RateLocation


class RateAreaRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_area_by_zip_code(self, zip_code: str) -> Optional[RateArea]:
        query = (
            select(RateArea)
            .join(RateLocation, RateLocation.area_id == RateArea.id)
            .where(RateLocation.zip_code == zip_code)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
