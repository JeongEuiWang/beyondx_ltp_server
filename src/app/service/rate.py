from typing import Optional
from ..schema.rate import RateLocationResponse
# from ..repository.rate_location import RateLocationRepository # UoW 통해 접근
from ..db.unit_of_work import UnitOfWork # UoW import
from typing import List


class RateService:
    def __init__(self, uow: UnitOfWork): # UoW 주입
        self.uow = uow

    async def get_rate_locations(
        self, region_id: int, city: Optional[str] = None, zip_code: Optional[str] = None
    ) -> List[RateLocationResponse]:
        async with self.uow: # UoW 컨텍스트 사용
            # RateLocationRepository는 UoW에 self.rate_locations로 등록
            locations = await self.uow.rate_location.get_rate_location_by_query(
            region_id, city, zip_code
        )
        return [RateLocationResponse.model_validate(loc) for loc in locations]
