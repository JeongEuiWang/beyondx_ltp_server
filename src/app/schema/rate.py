from pydantic import BaseModel

class BaseRateLocation(BaseModel):
    id: int
    area_id: int
    state: str
    county: str
    city: str
    zip_code: str
    class Config:
        from_attributes = True

# --------------------------------
# 지역 정보 조회
# --------------------------------
class RateLocationResponse(BaseRateLocation):
    pass
