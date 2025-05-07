from .._base import BaseSchema, IntegerIDSchema
from .._common import BaseUserSchema, BaseUserAddressSchema


class CheckEmailResponse(BaseSchema):
    is_unique: bool


class CreateUserResponse(BaseSchema):
    success: bool


class GetUserInfoResponse(IntegerIDSchema, BaseUserSchema):
    pass


class CreateUserAddressResponse(IntegerIDSchema, BaseUserAddressSchema):
    user_id: int


class GetUserAddressResponse(IntegerIDSchema, BaseUserAddressSchema):
    user_id: int
