from typing import Optional
from .._base import IntegerIDSchema
from .._common import BaseSchema

class CargoTransportationResponse(IntegerIDSchema, BaseSchema):
    name: str
    description: str


class CargoAccessorialResponse(IntegerIDSchema, BaseSchema):
    name: str
    description: str


class CargoPackageResponse(IntegerIDSchema, BaseSchema):
    name: str
    width: Optional[int] = None
    length: Optional[int] = None
    height: Optional[int] = None
