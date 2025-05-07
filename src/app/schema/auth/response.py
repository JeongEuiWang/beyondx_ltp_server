from .._common import AuthUserSchema
from .._base import IntegerIDSchema

class LoginResponse(IntegerIDSchema, AuthUserSchema):
    pass

class RefreshTokenResponse(IntegerIDSchema, AuthUserSchema):
    pass
