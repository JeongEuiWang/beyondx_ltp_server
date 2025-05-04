from pydantic import BaseModel, EmailStr, Field
from ._common import BaseUser


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
class GetUserInfoResponse(BaseUser):
    pass