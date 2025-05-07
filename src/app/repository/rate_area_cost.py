from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..model.rate import RateAreaCost


class RateAreaCostRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_area_costs(self, area_id: int) -> List[RateAreaCost]:
        query = select(RateAreaCost).where(RateAreaCost.area_id == area_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()
