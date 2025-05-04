from fastapi import APIRouter, Query, Depends, status, Path
from typing import Optional, List
from ..schema.rate import RateLocationResponse
from ..service._deps import rateServiceDeps

router = APIRouter(prefix="/rate", tags=["rate"])


@router.get(
    "/location/{region_id}",
    response_model=List[RateLocationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_locations_by_city_or_zip_code(
    rate_service: rateServiceDeps,
    region_id: int = Path(..., description="지역 ID"),
    city: Optional[str] = Query(None, description="도시명"),
    zip_code: Optional[str] = Query(None, description="우편번호"),
):
    return await rate_service.get_rate_locations(region_id, city, zip_code)
