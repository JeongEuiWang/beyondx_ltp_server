from pydantic import BaseModel, EmailStr, Field
from app.model._enum import UserLevelEnum


# --------------------------------
# 이메일 중복 확인
# --------------------------------
class CheckEmailResponse(BaseModel):
    is_unique: bool

    class Config:
        from_attributes = True


# --------------------------------
# 회원가입
# --------------------------------
class CreateUserRequest(BaseModel):
    email: EmailStr = Field(..., description="이메일")
    password: str = Field(..., description="비밀번호")
    first_name: str = Field(..., description="이름")
    last_name: str = Field(..., description="성")
    phone: str = Field(..., description="전화번호")


class CreateUserResponse(BaseModel):
    success: bool

    class Config:
        from_attributes = True


# --------------------------------
# 사용자 정보 조회
# --------------------------------
class UserLevel(BaseModel):
    id: int
    level: UserLevelEnum
    required_amount: float
    discount_rate: float


class GetUserInfoResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    total_payment_amount: float
    user_level: UserLevel

    class Config:
        from_attributes = True
