from typing import Optional
from ..schema.rate import RateLocationResponse
from ..db.unit_of_work import UnitOfWork
from typing import List


class RateService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_rate_locations(
        self, region_id: int, city: Optional[str] = None, zip_code: Optional[str] = None
    ) -> List[RateLocationResponse]:
        async with self.uow:
            locations = await self.uow.rate_location.get_rate_location_by_query(
                region_id, city, zip_code
            )
            if not locations:
                return []
        return [RateLocationResponse.model_validate(loc) for loc in locations]
