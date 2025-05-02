from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ..model.rate import RateLocation


class RateRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_rate_locations_by_region(
        self, region_id: int, city: Optional[str] = None, zip_code: Optional[str] = None
    ) -> List[RateLocation]:
        """
        지역 정보 조회
        """
        pass
