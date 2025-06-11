from datetime import datetime
from decimal import Decimal

from ...core.utils import round_up_decimal
from ...schema.cost import BaseCostSchema, ExtraCostSchema
from ...schema import QuoteLocationSchema


class ExtraCostBuilder:
    def __init__(self, base_cost: BaseCostSchema):
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
        return max(
            Decimal(25),
            round_up_decimal(self._base_cost.freight_weight * Decimal("0.02")),
        )

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
        if request_datetime.weekday() >= 5:
            return Decimal(100)
        else:
            return Decimal(0)

    def _check_after_hour_cost(self, request_datetime: datetime) -> Decimal:
        if request_datetime.hour >= 17:
            return Decimal(100)
        else:
            return Decimal(0)

    def _check_priority_with_date(
        self, is_priority: bool, request_datetime: datetime
    ) -> Decimal:
        if is_priority and (9 <= request_datetime.hour < 17):
            return Decimal(100)
        else:
            return Decimal(0)

    def calculate(self) -> ExtraCostSchema:
        result = {
            "cost": self._final_cost,
        }
        return ExtraCostSchema.model_validate(result)
