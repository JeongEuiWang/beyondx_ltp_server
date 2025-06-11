from fastapi import APIRouter, status, Depends
from typing import List
from ..schema.cargo import CargoTransportationResponse, CargoAccessorialResponse, CargoPackageResponse
from ..service import CargoService
from ..core.uow import get_uow
from ..db.unit_of_work import UnitOfWork

router = APIRouter(prefix="/cargo", tags=["cargo"])


@router.get(
    "/transportation",
    response_model=List[CargoTransportationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_cargo_transportation(
    uow: UnitOfWork = Depends(get_uow),
):
    cargo_service = CargoService(uow)
    return await cargo_service.get_cargo_transportation()


@router.get(
    "/accessorial",
    response_model=List[CargoAccessorialResponse],
    status_code=status.HTTP_200_OK,
)
async def get_cargo_accessorial(
    uow: UnitOfWork = Depends(get_uow),
):
    cargo_service = CargoService(uow)
    return await cargo_service.get_cargo_accessorial()


@router.get(
    "/package",
    response_model=List[CargoPackageResponse],
    status_code=status.HTTP_200_OK,
)
async def get_cargo_package(
    uow: UnitOfWork = Depends(get_uow),
):
    cargo_service = CargoService(uow)
    return await cargo_service.get_cargo_package()
