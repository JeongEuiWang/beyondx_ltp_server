from .._common import BaseUserAddressSchema
from .._base import BaseSchema
from pydantic import EmailStr

class CreateUserRequest(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    password: str


class CreateUserAddressRequest(BaseUserAddressSchema):
    pass
