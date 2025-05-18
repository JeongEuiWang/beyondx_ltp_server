from fastapi import APIRouter, Query, Depends, status, Path
from typing import Optional, List
from ..schema.rate import RateLocationResponse
from ..service import RateService
from ..core.uow import get_uow
from ..db.unit_of_work import UnitOfWork

router = APIRouter(prefix="/rate", tags=["rate"])


@router.get(
    "/location/{region_id}",
    response_model=List[RateLocationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_locations_by_city_or_zip_code(
    uow: UnitOfWork = Depends(get_uow),
    region_id: int = Path(..., description="지역 ID"),
    city: Optional[str] = Query(None, description="도시명"),
    zip_code: Optional[str] = Query(None, description="우편번호"),
):
    rate_service = RateService(uow)
    return await rate_service.get_rate_locations(region_id, city, zip_code)
