from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# --------------------------------
# 공통
# --------------------------------
class BaseToken(BaseModel):
    token: str
    expires_at: datetime

    class Config:
        from_attributes = True


class BaseUser(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    total_payment_amount: float
    user_level_id: int

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
    email: EmailStr = Field(..., description="이메일")
    password: str = Field(..., description="비밀번호")


class LoginResponse(AuthUser):
    pass


# --------------------------------
# 토큰 리프레시
# --------------------------------
class RefreshTokenResponse(AuthUser):
    pass
