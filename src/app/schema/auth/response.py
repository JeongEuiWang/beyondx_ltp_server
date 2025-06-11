from .._common import AuthUserSchema
from .._base import IntegerIDSchema, BaseSchema

class LoginResponse(IntegerIDSchema, AuthUserSchema):
    pass

class RefreshTokenResponse(IntegerIDSchema, AuthUserSchema):
    pass

class LogoutResponse(BaseSchema):
    success: bool
    message: str
