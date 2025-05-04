from fastapi import APIRouter, Query, Depends, status, Path
from typing import Optional, List
from ..schema.rate import RateLocationResponse
from ..service._deps import rateServiceDeps

router = APIRouter(prefix="/rate", tags=["rate"])


@router.get(
    "/location",
    response_model=List[RateLocationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_locations_by_city_or_zip_code(
    rate_service: rateServiceDeps,
    city: Optional[str] = Query(None, description="도시명"),
    zip_code: Optional[str] = Query(None, description="우편번호"),
):
    return await rate_service.get_locations(city, zip_code)


@router.get(
    "/location/{region_id}",
    response_model=List[RateLocationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_rate_location(
    rate_service: rateServiceDeps,
    region_id: int = Path(..., description="지역 ID"),
):
    return await rate_service.get_region_locations(region_id)
