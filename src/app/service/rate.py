from fastapi import HTTPException
from typing import Optional
from ..schema.rate import RateLocationResponse, GetRateLocationListResponse
from ..repository.rate import RateRepository


class RateService:
    def __init__(self, rate_repository: RateRepository):
        self.rate_repository = rate_repository

    async def get_rate_locations(
        self, region_id: int, city: Optional[str] = None, zip_code: Optional[str] = None
    ) -> GetRateLocationListResponse:
        """
        지역 정보 조회
        """
        pass
