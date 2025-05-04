from fastapi import APIRouter, Query, Depends, status, Path
from typing import Optional, List
from ..service._deps import cargoServiceDeps
from ..schema.cargo import CargoTransportationResponse, CargoAccessorialResponse
router = APIRouter(prefix="/cargo", tags=["cargo"])

@router.get(
    "/transportation",
    response_model=List[CargoTransportationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_cargo_transportation(
    cargo_service: cargoServiceDeps,
):
    return await cargo_service.get_cargo_transportation()

@router.get(
    "/accessorial",
    response_model=List[CargoAccessorialResponse],
    status_code=status.HTTP_200_OK,
)
async def get_cargo_accessorial(
    cargo_service: cargoServiceDeps,
):
    return await cargo_service.get_cargo_accessorial()