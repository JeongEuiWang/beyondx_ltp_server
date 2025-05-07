from pydantic import EmailStr
from .._base import BaseSchema

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str
