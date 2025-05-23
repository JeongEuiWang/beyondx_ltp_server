from pydantic import EmailStr
from app.model._enum import LocationTypeEnum, UserLevelEnum
from .._base import BaseSchema, IntegerIDSchema


class UserLevelSchema(IntegerIDSchema):
    level: UserLevelEnum
    required_amount: float
    discount_rate: float


class CheckEmailResponse(BaseSchema):
    is_unique: bool


class CreateUserResponse(BaseSchema):
    success: bool


class GetUserInfoResponse(IntegerIDSchema):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    total_payment_amount: float
    user_level: UserLevelSchema


class CreateUserAddressResponse(IntegerIDSchema):
    user_id: int
    name: str
    state: str
    city: str
    county: str
    zip_code: str
    location_type: LocationTypeEnum
    address: str


class GetUserAddressResponse(IntegerIDSchema):
    user_id: int
    name: str
    state: str
    city: str
    county: str
    zip_code: str
    location_type: LocationTypeEnum
    address: str