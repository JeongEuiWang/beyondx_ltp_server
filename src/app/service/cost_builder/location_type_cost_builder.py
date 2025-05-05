from pprint import pprint
from typing import List, Literal, Optional, Dict, Any
from decimal import Decimal

from app.core.utils import round_up_decimal
from app.model._enum import LocationTypeEnum
from app.schema.cost import BaseCost, LocationCost


class LocationCostBuilder:
    # 위치 유형별 비용 상수
    RESIDENTIAL_COST = Decimal(25)

    # 공항 픽업/배송 비용 설정
    AIRPORT_CONFIG = {
        "PICK_UP": {
            "min_cost": Decimal(30),
            "max_cost": Decimal(200),
            "price_per_weight": Decimal(0.035),
        },
        "DELIVERY": {
            "min_cost": Decimal(25),
            "max_cost": Decimal(200),
            "price_per_weight": Decimal(0.03),
        },
    }

    def __init__(self, base_cost: BaseCost):
        self._base_cost = base_cost
        self._final_cost = Decimal(0)

    def check_location_type(
        self,
        location_type: LocationTypeEnum,
        delivery_type: Literal["PICK_UP", "DELIVERY"],
    ) -> "LocationCostBuilder":
        if location_type == LocationTypeEnum.RESIDENTIAL:
            self._final_cost += self.RESIDENTIAL_COST
        elif location_type == LocationTypeEnum.AIRPORT:
            self._final_cost += round_up_decimal(self._calculate_airport_cost(delivery_type))
        else:
            self._final_cost += Decimal(0)

        return self

    def _calculate_airport_cost(
        self, delivery_type: Literal["PICK_UP", "DELIVERY"]
    ) -> Decimal:
        config = self.AIRPORT_CONFIG[delivery_type]
        min_cost = config["min_cost"]
        max_cost = config["max_cost"]
        price_per_weight = config["price_per_weight"]

        cost_with_weight = price_per_weight * self._base_cost.freight_weight

        if cost_with_weight > max_cost:
            return max_cost
        elif cost_with_weight < min_cost:
            return min_cost
        else:
            return cost_with_weight

    def calculate(self) -> LocationCost:
        return LocationCost(cost=self._final_cost)
