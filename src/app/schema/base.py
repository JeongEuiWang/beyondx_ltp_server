from typing import ClassVar
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """모든 스키마의 기본 클래스"""
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,  # 이전의 orm_mode=True 대체
        validate_assignment=True,
        extra="forbid"
    )