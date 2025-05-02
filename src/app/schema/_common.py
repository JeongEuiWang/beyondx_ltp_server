from pydantic import BaseModel
from pydantic import EmailStr


class BaseUser(BaseModel):
    id: int
    email: EmailStr
    role_id: int
    first_name: str
    last_name: str
    phone: str
    total_payment_amount: float
    user_level_id: int

    class Config:
        from_attributes = True
