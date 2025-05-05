from decimal import Decimal

from app.repository.rate import RateRepository
from app.repository.user import UserRepository
from app.repository.user_level import UserLevelRepository
from app.schema.quote import QuoteLocationRequest
from app.service.cost_builder import (
    BaseCostBuilder,
    ExtraCostBuilder,
    LocationCostBuilder,
    DiscountBuilder,
)
from app.schema.cost import BaseCost, DiscountCost, ExtraCost, LocationCost


class CostService:
    def __init__(
        self,
        rate_repository: RateRepository,
        user_repository: UserRepository,
        user_level_repository: UserLevelRepository,
    ):
        self.rate_repository = rate_repository
        self.user_level_repository = user_level_repository
        self.user_repository = user_repository

    async def calculate_base_cost(
        self,
        cargo_list,
        from_location: QuoteLocationRequest,
        to_location: QuoteLocationRequest,
    ) -> BaseCost:
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        for cargo in cargo_list:
            builder.set_freight_weight(
                cargo.weight, cargo.quantity, cargo.width, cargo.height, cargo.length
            )

        # 지역 요율 계산
        from_location_area = await self.rate_repository.get_area_by_zip_code(
            from_location.zip_code
        )
        to_location_area = await self.rate_repository.get_area_by_zip_code(
            to_location.zip_code
        )

        if from_location_area is None or to_location_area is None:
            raise Exception("지역 요율 계산 중 오류가 발생했습니다.")

        # 현재 DB 기준 id 값이 클 수록 먼 지역, 이 기준은 변동될 수 있음
        base_area = (
            from_location_area
            if from_location_area.id >= to_location_area.id
            else to_location_area
        )
        base_area_id = base_area.id

        area_costs = await self.rate_repository.get_area_costs(base_area_id)

        builder.set_location_rate(
            min_load=base_area.min_load,
            max_load=base_area.max_load,
            max_load_weight=base_area.max_load_weight,
        )

        builder.set_price_per_weight(area_costs)
        builder.calculate_base_cost()
        builder.calculate_with_fsc()

        return builder.calculate()

    async def calculate_location_type_cost(
        self,
        from_location: QuoteLocationRequest,
        to_location: QuoteLocationRequest,
        base_cost: BaseCost,
    ) -> LocationCost:
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(from_location.location_type, "PICK_UP")
        builder.check_location_type(to_location.location_type, "DELIVERY")

        return builder.calculate()

    async def calculate_extra_cost(
        self,
        is_priority: bool,
        from_location: QuoteLocationRequest,
        to_location: QuoteLocationRequest,
        base_cost: BaseCost,
    ) -> ExtraCost:
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_accesserial(from_location)
        builder.calculate_accesserial(to_location)
        builder.calculate_service_extra_cost(is_priority, from_location)
        builder.calculate_service_extra_cost(is_priority, to_location)
        return builder.calculate()

    async def calculate_discount(
        self,
        user_id: int,
        total_cost: Decimal,
    ) -> DiscountCost:
        builder = DiscountBuilder(total_cost=total_cost)
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise Exception("사용자 조회 중 오류가 발생했습니다.")

        user_level = await self.user_level_repository.get_level_by_id(
            user.user_level_id
        )
        if user_level is None:
            raise Exception("사용자 레벨 조회 중 오류가 발생했습니다.")

        builder.calculate_discount(user_level)

        return builder.calculate()
