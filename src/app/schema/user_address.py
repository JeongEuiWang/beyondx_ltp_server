from pydantic import BaseModel, Field
from typing import List
from app.model._enum import LocationTypeEnum


# --------------------------------
# 사용자 주소 생성
# --------------------------------
class CreateUserAddressRequest(BaseModel):
    name: str = Field(..., description="주소 별칭")
    state: str = Field(..., description="주(State)")
    city: str = Field(..., description="도시(City)")
    county: str = Field(..., description="카운티(County)")
    zip_code: str = Field(..., description="우편번호")
    address: str = Field(..., description="상세주소")


class CreateUserAddressResponse(BaseModel):
    success: bool

    class Config:
        from_attributes = True


# --------------------------------
# 사용자 주소 조회
# --------------------------------
class UserAddressResponse(BaseModel):
    id: int
    name: str
    state: str
    city: str
    county: str
    zip_code: str
    location_type: LocationTypeEnum
    address: str

    class Config:
        from_attributes = True


class GetUserAddressListResponse(BaseModel):
    addresses: List[UserAddressResponse]

    class Config:
        from_attributes = True
