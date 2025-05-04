from pydantic import BaseModel
from app.model._enum import UserLevelEnum


# --------------------------------
# 사용자 레벨 조회
# --------------------------------
class UserLevelResponse(BaseModel):
    id: int
    user_level: UserLevelEnum
    required_amount: float
    discount_rate: float

    class Config:
        from_attributes = True
