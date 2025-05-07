from .._base import IntegerIDSchema
from .._common import BaseSchema

class CargoTransportationResponse(IntegerIDSchema, BaseSchema):
    name: str
    description: str


class CargoAccessorialResponse(IntegerIDSchema, BaseSchema):
    name: str
    description: str
