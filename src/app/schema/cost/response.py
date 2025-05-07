from dataclasses import dataclass
from decimal import Decimal
from ...schema._base import BaseSchema

    
class CostModelSchema(BaseSchema):
    cost: Decimal

class BaseCostSchema(CostModelSchema):
    freight_weight: Decimal
    is_max_load: bool

class ExtraCostSchema(CostModelSchema):
    pass

class LocationCostSchema(CostModelSchema):
    pass

class DiscountCostSchema(CostModelSchema):
  pass

