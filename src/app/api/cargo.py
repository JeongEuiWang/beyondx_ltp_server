from fastapi import APIRouter, status
from typing import List
from ..schema.cargo import CargoTransportationResponse, CargoAccessorialResponse
from ..core.dependencies import container
from ..service import CargoService

router = APIRouter(prefix="/cargo", tags=["cargo"])


@router.get(
    "/transportation",
    response_model=List[CargoTransportationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_cargo_transportation(
    cargo_service: CargoService = container.get("cargo_service"),
):
    return await cargo_service.get_cargo_transportation()


@router.get(
    "/accessorial",
    response_model=List[CargoAccessorialResponse],
    status_code=status.HTTP_200_OK,
)
async def get_cargo_accessorial(
    cargo_service: CargoService = container.get("cargo_service"),
):
    return await cargo_service.get_cargo_accessorial()
