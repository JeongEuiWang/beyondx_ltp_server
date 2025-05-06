from ._common import CommonUserSchema, CommonUserAddressSchema


class CreateUserRequest(CommonUserSchema):
    password: str


class CreateUserAddressRequest(CommonUserAddressSchema):
    pass
