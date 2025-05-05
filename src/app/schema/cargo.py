from pydantic import BaseModel

class CargoTransportationResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True


class CargoAccessorialResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True
