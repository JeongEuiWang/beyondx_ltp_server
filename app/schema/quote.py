from typing import Optional, List
from pydantic import BaseModel

class CreateQuoteRequest(BaseModel):
    # 기존 CreateQuoteRequest 코드 유지
    # ... existing code ...

class UpdateQuoteRequest(BaseModel):
    cargo: Optional[List[dict]] = None
    from_location: Optional[dict] = None
    to_location: Optional[dict] = None
    is_priority: Optional[bool] = None 