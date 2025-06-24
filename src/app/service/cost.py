from decimal import Decimal
from typing import List

from ..db.unit_of_work import UnitOfWork
from ..schema import QuoteLocationSchema, QuoteCargoSchema
from ..service.cost_builder import (
    BaseCostBuilder,
    ExtraCostBuilder,
    LocationCostBuilder,
    DiscountBuilder,
)
from ..schema.cost import (
    BaseCostSchema,
    DiscountCostSchema,
    ExtraCostSchema,
    LocationCostSchema,
)
from ..core.exceptions import NotFoundException


class CostService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    # FTL 선택 시 즉시 max_load 값으로 계산되어야 함
    async def calculate_base_cost(
        self,
        cargo_transportation_id: int,
        cargo_list: List[QuoteCargoSchema],
        from_location: QuoteLocationSchema,
        to_location: QuoteLocationSchema,
    ) -> BaseCostSchema:
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        async with self.uow:
            for cargo in cargo_list:
                builder.set_freight_weight(
                    cargo.weight, cargo.quantity, cargo.width, cargo.height, cargo.length
                )

            from_location_area = await self.uow.rate_area.get_area_by_zip_code(
                from_location.zip_code
            )
            to_location_area = await self.uow.rate_area.get_area_by_zip_code(
                to_location.zip_code
            )

            if from_location_area is None or to_location_area is None:
                raise NotFoundException(message="지역 요율 정보를 찾을 수 없습니다.")

            base_area = (
                from_location_area
                if from_location_area.id >= to_location_area.id
                else to_location_area
            )
            builder.set_location_rate(
                min_load=base_area.min_load,
                max_load=base_area.max_load,
                max_load_weight=base_area.max_load_weight,
            )
            base_area_id = base_area.id
            area_costs = await self.uow.rate_area_cost.get_area_costs(
                base_area_id
            )

            if cargo_transportation_id == 2: # FTL
                builder.calculate_ftl_cost()
            else: # LTL
                builder.set_price_per_weight(area_costs)
                builder.calculate_base_cost()
            
            builder.calculate_with_fsc()
            
            # 개별 화물에 대한 계산 결과를 가져옵니다.
            cargo_cost_schema = builder.calculate()
            
            # 계산된 비용과 무게를 전체 합계에 누적합니다.
            total_cost = cargo_cost_schema.cost
            total_freight_weight = cargo_cost_schema.freight_weight
            is_any_max_load = cargo_cost_schema.is_max_load

        # 합산된 결과로 최종 BaseCostSchema를 생성하여 반환합니다.
        return BaseCostSchema(
            cost=total_cost,
            freight_weight=total_freight_weight,
            is_max_load=is_any_max_load,
        )

    async def calculate_location_type_cost(
        self,
        from_location: QuoteLocationSchema,
        to_location: QuoteLocationSchema,
        base_cost: BaseCostSchema,
    ) -> LocationCostSchema:
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(from_location.location_type, "PICK_UP")
        builder.check_location_type(to_location.location_type, "DELIVERY")

        return builder.calculate()

    async def calculate_extra_cost(
        self,
        is_priority: bool,
        from_location: QuoteLocationSchema,
        to_location: QuoteLocationSchema,
        base_cost: BaseCostSchema,
    ) -> ExtraCostSchema:
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
    ) -> DiscountCostSchema:
        builder = DiscountBuilder(total_cost=total_cost)
        async with self.uow:
            user = await self.uow.user.get_user_by_id(user_id)
            if user is None:
                raise NotFoundException(message=f"사용자 ID {user_id}를 찾을 수 없습니다.")

            user_level = await self.uow.user_level.get_level_by_id(
                user.user_level_id
            )
            if user_level is None:
                raise NotFoundException(message=f"사용자 등급 ID {user.user_level_id}를 찾을 수 없습니다.")

            builder.calculate_discount(user_level)
        return builder.calculate()
