from decimal import Decimal

from app.model.user import UserLevel
from app.schema.cost import DiscountCost

class DiscountBuilder:
    def __init__(self, total_cost: Decimal):
        self._total_cost = total_cost
        
    def calculate_discount(
        self, user_level: UserLevel
    ) -> "DiscountBuilder":
        if user_level.discount_rate > 0:
            self._total_cost -= self._calculate_discount(user_level.discount_rate)
        return self
    
    def _calculate_discount(self, discount_rate: Decimal) -> Decimal:
        return self._total_cost * discount_rate
    
    def calculate(self) -> DiscountCost:
        return DiscountCost(cost=self._total_cost)