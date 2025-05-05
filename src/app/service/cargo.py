from fastapi import HTTPException
from typing import Optional
from ..schema.cargo import CargoTransportationResponse, CargoAccessorialResponse
from ..repository.cargo import CargoRepository
from typing import List


class CargoService:
    def __init__(self, cargo_repository: CargoRepository):
        self.cargo_repository = cargo_repository

    async def get_cargo_transportation(
        self,
    ) -> List[CargoTransportationResponse]:
        locations = await self.cargo_repository.get_cargo_transportation()
        return [CargoTransportationResponse.model_validate(loc) for loc in locations]

    async def get_cargo_accessorial(
        self,
    ) -> List[CargoAccessorialResponse]:
        accessorials = await self.cargo_repository.get_cargo_accessorial()
        return [CargoAccessorialResponse.model_validate(acc) for acc in accessorials]
