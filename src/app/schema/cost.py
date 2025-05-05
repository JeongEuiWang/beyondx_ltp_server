from dataclasses import dataclass
from decimal import Decimal

from pydantic import BaseModel


@dataclass
class RateCost:
    min_weight: Decimal
    max_weight: Decimal
    price_per_weight: Decimal
    
class CostModel(BaseModel):
    cost: Decimal

class BaseCost(CostModel):
    freight_weight: Decimal
    is_max_load: bool

class ExtraCost(CostModel):
    pass

class LocationCost(CostModel):
    pass

