from pydantic import EmailStr
from app.schema.base import BaseSchema
from app.model._enum import LocationTypeEnum  

class CommonUserSchema(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str


class CommonUserAddressSchema(BaseSchema):
    name: str
    state: str
    city: str
    county: str
    zip_code: str
    location_type: LocationTypeEnum
    address: str
