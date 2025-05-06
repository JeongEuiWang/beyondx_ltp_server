from datetime import datetime
from decimal import Decimal

from app.core.utils import round_up_decimal
from app.schema.cost import BaseCost, ExtraCost
from app.schema.quote import QuoteLocationSchema


class ExtraCostBuilder:
    def __init__(self, base_cost: BaseCost):
        self._base_cost = base_cost
        self._final_cost = Decimal(0)

    def calculate_accesserial(
        self, location: QuoteLocationSchema
    ) -> "ExtraCostBuilder":
        if len(location.accessorials) > 0:
            for accessory in location.accessorials:
                if accessory.name == "Inside Delivery":
                    self._final_cost += self._calculate_inside_delivery_cost()
                elif accessory.name == "Two Person":
                    self._final_cost += self._calculate_two_person_cost()
                elif accessory.name == "Lift Gate":
                    self._final_cost += self._calculate_lift_gate_cost()
        return self

    def _calculate_inside_delivery_cost(self) -> Decimal:
        return max(Decimal(25), round_up_decimal(self._base_cost.freight_weight * Decimal("0.02")))

    def _calculate_two_person_cost(self) -> Decimal:
        return Decimal(80)

    def _calculate_lift_gate_cost(self) -> Decimal:
        return Decimal(25)

    def calculate_service_extra_cost(
        self, is_priority: bool, location: QuoteLocationSchema
    ) -> "ExtraCostBuilder":

        self._final_cost += self._check_weekend_cost(location.request_datetime)
        self._final_cost += self._check_after_hour_cost(location.request_datetime)
        self._final_cost += self._check_priority_with_date(
            is_priority, location.request_datetime
        )
        return self

    def _check_weekend_cost(self, request_datetime: datetime) -> Decimal:
        # 주말 확인 (토요일 또는 일요일)
        if request_datetime.weekday() >= 5:  # 5: 토요일, 6: 일요일
            return Decimal(100)
        else:
            return Decimal(0)

    def _check_after_hour_cost(self, request_datetime: datetime) -> Decimal:
        # 17시 이후인 경우 (After Hour)
        if request_datetime.hour >= 17:
            return Decimal(100)
        else:
            return Decimal(0)

    def _check_priority_with_date(
        self, is_priority: bool, request_datetime: datetime
    ) -> Decimal:
        # is_priority이고 업무 시간(9-17시)인 경우
        if is_priority and (9 <= request_datetime.hour < 17):
            return Decimal(100)
        else:
            return Decimal(0)

    def calculate(self) -> ExtraCost:
        return ExtraCost(cost=self._final_cost)
