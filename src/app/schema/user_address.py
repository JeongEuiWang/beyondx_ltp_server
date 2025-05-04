from pydantic import BaseModel, Field
from typing import List
from app.model._enum import LocationTypeEnum, UserLevelEnum

# --------------------------------
# 사용자 주소 공통
# --------------------------------
class BaseUserAddress(BaseModel):
    name: str
    state: str
    city: str
    county: str
    zip_code: str
    location_type: LocationTypeEnum
    address: str
    class Config:
        from_attributes = True


# --------------------------------
# 사용자 주소 생성
# --------------------------------
class CreateUserAddressRequest(BaseModel):
    name: str = Field(..., description="주소 별칭")
    state: str = Field(..., description="주(State)")
    city: str = Field(..., description="도시(City)")
    county: str = Field(..., description="카운티(County)")
    zip_code: str = Field(..., description="우편번호")
    location_type: LocationTypeEnum = Field(..., description="위치 타입")
    address: str = Field(..., description="상세주소")


class CreateUserAddressResponse(BaseUserAddress):
    id: int
    user_id: int


# --------------------------------
# 사용자 주소 조회
# --------------------------------
class UserAddressResponse(BaseUserAddress):
    id: int
    user_id: int

    class Config:
        from_attributes = True
