from ..schema.cargo import CargoTransportationResponse, CargoAccessorialResponse, CargoPackageResponse
from ..db.unit_of_work import UnitOfWork
from typing import List


class CargoService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_cargo_transportation(
        self,
    ) -> List[CargoTransportationResponse]:
        async with self.uow:
            locations = await self.uow.cargo.get_cargo_transportation()
            return [CargoTransportationResponse.model_validate(loc) for loc in locations]

    async def get_cargo_accessorial(
        self,
    ) -> List[CargoAccessorialResponse]:
        async with self.uow:
            accessorials = await self.uow.cargo.get_cargo_accessorial()
            return [CargoAccessorialResponse.model_validate(acc) for acc in accessorials]

    async def get_cargo_package(
        self,
    ) -> List[CargoPackageResponse]:
        async with self.uow:
            packages = await self.uow.cargo.get_cargo_package()
            return [CargoPackageResponse.model_validate(pkg) for pkg in packages]
