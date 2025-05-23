from ..schema.cargo import CargoTransportationResponse, CargoAccessorialResponse
from ..db.unit_of_work import UnitOfWork
from typing import List


class CargoService:
    def __init__(self, uow: UnitOfWork): # UoW 주입
        self.uow = uow

    async def get_cargo_transportation(
        self,
    ) -> List[CargoTransportationResponse]:
        async with self.uow: # UoW 컨텍스트 사용
            # CargoRepository는 UoW에 self.cargos로 등록되어 있음
            locations = await self.uow.cargo.get_cargo_transportation()
            return [CargoTransportationResponse.model_validate(loc) for loc in locations]

    async def get_cargo_accessorial(
        self,
    ) -> List[CargoAccessorialResponse]:
        async with self.uow: # UoW 컨텍스트 사용
            accessorials = await self.uow.cargo.get_cargo_accessorial()
            return [CargoAccessorialResponse.model_validate(acc) for acc in accessorials]
