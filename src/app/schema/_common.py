from pydantic import EmailStr
from ._base import BaseSchema, IntegerIDSchema, StringIDSchema
from app.model._enum import OrderStatusEnum, UserLevelEnum, LocationTypeEnum
from datetime import datetime
from typing import List


class BaseUserLevelSchema(IntegerIDSchema):
    level: UserLevelEnum
    required_amount: float
    discount_rate: float


class BaseUserSchema(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    total_payment_amount: float
    role_id: int
    user_level: BaseUserLevelSchema


class BaseTokenSchema(BaseSchema):
    token: str
    expires_at: datetime


class AccessTokenSchema(BaseSchema):
    access: BaseTokenSchema


class AuthUserSchema(BaseUserSchema, AccessTokenSchema):
    pass


class BaseUserAddressSchema(BaseSchema):
    name: str
    state: str
    city: str
    county: str
    zip_code: str
    location_type: LocationTypeEnum
    address: str


class BaseRateLocationSchema(BaseSchema):
    area_id: int
    state: str
    county: str
    city: str
    zip_code: str


class BaseQuoteSchema(StringIDSchema, BaseSchema):
    user_id: int
    cargo_transportation_id: int
    is_priority: bool
    total_weight: float
    base_price: float
    extra_price: float
    total_price: float
    order_status: OrderStatusEnum
    order_primary: str | None
    order_additional_request: str | None
    created_at: datetime


class QuoteLocationAccessorialSchema(BaseSchema):
    cargo_accessorial_id: int
    name: str


class QuoteLocationSchema(BaseSchema):
    state: str
    county: str
    city: str
    zip_code: str
    address: str
    location_type: LocationTypeEnum
    request_datetime: datetime
    accessorials: List[QuoteLocationAccessorialSchema]


class QuoteCargoSchema(BaseSchema):
    width: int
    length: int
    height: int
    weight: int
    quantity: int
    package_description: str
    cargo_stackable: bool
    cargo_temperature: str
    is_hazardous: bool
    hazardous_detail: str
