from typing import List
from decimal import Decimal
from dataclasses import dataclass
from ...core.utils import round_up_decimal
from ...schema.cost import BaseCostSchema


@dataclass
class RateCost:
    min_weight: Decimal
    max_weight: Decimal
    price_per_weight: Decimal

class BaseCostBuilder:
    def __init__(self, fsc: Decimal):
        self._freight_weight = Decimal(
            "0"
        )  # 최종 운임 무게, 각 Cargo마다 무게 / 부피 무게 비교 후 큰값 사용
        self._min_load = Decimal("0")
        self._max_load = Decimal("0")
        self._max_load_weight = Decimal("0")
        self._price_per_weight = Decimal("0")
        self._is_max_load = False
        self._freight_cost = Decimal("0")
        self._fsc = fsc
        self._final_cost = Decimal("0")

    # 운임 무게 계산, 각 cargo마다 실행하여 총 freight_weight 계산
    def set_freight_weight(
        self, weight: float, quantity: int, width: float, height: float, length: float
    ) -> "BaseCostBuilder":
        volume_weight = self._calculate_volume_weight(width, height, length)
        package_weight = self._calculate_package_weight(weight, quantity)
        self._freight_weight = max(package_weight, volume_weight)
        return self

    def _calculate_package_weight(self, weight: float, quantity: int) -> Decimal:
        return round_up_decimal(Decimal(weight * quantity))

    def _calculate_volume_weight(
        self, width: float, height: float, length: float
    ) -> Decimal:
        return round_up_decimal(Decimal(width * height * length / 166))

    # 지역 요율 계산, Area 확정은 Service 레이어에서 결정
    def set_location_rate(
        self,
        min_load: Decimal,
        max_load: Decimal,
        max_load_weight: Decimal,
    ) -> "BaseCostBuilder":
        self._min_load = min_load
        self._max_load = max_load
        self._max_load_weight = max_load_weight
        return self

    def set_price_per_weight(self, rate_costs: List[RateCost]) -> "BaseCostBuilder":
        if self._freight_weight > self._max_load_weight:
            raise Exception(
                "최대 운임 무게를 초과했습니다. 고객사에 직접 문의해주세요."
            )
        for rate_cost in rate_costs:
            if (
                self._freight_weight >= rate_cost.min_weight
                and self._freight_weight <= rate_cost.max_weight
            ):
                self._price_per_weight = rate_cost.price_per_weight
                break
        return self

    def calculate_base_cost(self) -> "BaseCostBuilder":
        base_freight_cost = self._freight_weight * self._price_per_weight
        if base_freight_cost > self._max_load:
            self._is_max_load = True
            self._freight_cost = self._max_load
        elif base_freight_cost < self._min_load:
            self._freight_cost = self._min_load
        else:
            self._freight_cost = base_freight_cost
        return self

    def calculate_with_fsc(self) -> "BaseCostBuilder":
        self._final_cost = round_up_decimal(self._freight_cost * (1 + self._fsc))
        return self

    def calculate(self) -> BaseCostSchema:
        result = {
          "cost": self._final_cost,
          "freight_weight": self._freight_weight,
          "is_max_load": self._is_max_load,
        }
        return BaseCostSchema.model_validate(result)

