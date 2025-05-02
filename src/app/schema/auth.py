from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from ._common import BaseUser


# --------------------------------
# 공통
# --------------------------------
class BaseToken(BaseModel):
    token: str
    expires_at: datetime

    class Config:
        from_attributes = True


class AccessToken(BaseModel):
    access: BaseToken

    class Config:
        from_attributes = True


class AuthUser(BaseUser, AccessToken):
    pass


# --------------------------------
# 로그인
# --------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(AuthUser):
    pass


# --------------------------------
# 토큰 리프레시
# --------------------------------
class RefreshTokenResponse(AuthUser):
    pass
