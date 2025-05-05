from fastapi import HTTPException
from typing import Optional
from ..schema.rate import RateLocationResponse
from ..repository.rate import RateRepository
from typing import List


class RateService:
    def __init__(self, rate_repository: RateRepository):
        self.rate_repository = rate_repository

    async def get_rate_locations(
        self, region_id: int, city: Optional[str] = None, zip_code: Optional[str] = None
    ) -> List[RateLocationResponse]:
        locations = await self.rate_repository.get_rate_location_by_query(
            region_id, city, zip_code
        )
        return [RateLocationResponse.model_validate(loc) for loc in locations]
