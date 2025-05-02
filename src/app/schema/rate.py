from pydantic import BaseModel
from typing import List


# --------------------------------
# 지역 정보 조회
# --------------------------------
class RateLocationResponse(BaseModel):
    id: int
    area_id: int
    state: str
    county: str
    city: str
    zip_code: str

    class Config:
        from_attributes = True


class GetRateLocationListResponse(BaseModel):
    locations: List[RateLocationResponse]

    class Config:
        from_attributes = True
