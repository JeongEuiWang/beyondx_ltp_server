from pydantic import BaseModel

class BaseCargoTransportation(BaseModel):
    id: int
    name: str
    description: str
    class Config:
        from_attributes = True

class CargoTransportationResponse(BaseCargoTransportation):
    pass

class BaseCargoAccessorial(BaseModel):
    id: int
    name: str
    description: str
    class Config:
        from_attributes = True

class CargoAccessorialResponse(BaseCargoAccessorial):
    pass