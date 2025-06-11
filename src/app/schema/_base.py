from typing import ClassVar
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class BaseSchema(BaseModel):
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True, 
        validate_assignment=True,
        extra="forbid",
        json_encoders={
            Decimal: float
        }
    )

class IntegerIDSchema(BaseSchema):
    id: int

class StringIDSchema(BaseSchema):
    id: str
