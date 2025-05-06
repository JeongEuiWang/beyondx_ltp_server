from ..base import BaseSchema
from app.model._enum import UserLevelEnum
from ._common import CommonUserSchema, CommonUserAddressSchema


class CheckEmailResponse(BaseSchema):
    is_unique: bool


class CreateUserResponse(CommonUserSchema):
    success: bool


class UserLevelResponse(BaseSchema):
    id: int
    level: UserLevelEnum
    required_amount: float
    discount_rate: float


class GetUserInfoResponse(CommonUserSchema):
    id: int
    total_payment_amount: float
    user_level: UserLevelResponse


class CreateUserAddressResponse(CommonUserAddressSchema):
    id: int
    user_id: int


class GetUserAddressResponse(CommonUserAddressSchema):
    id: int
    user_id: int
