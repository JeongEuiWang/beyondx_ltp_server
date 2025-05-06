import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.model._enum import LocationTypeEnum, OrderStatusEnum 

class BaseQuoteRequest(BaseModel):
  cargo_transportation_id: int
  is_priority: bool
  # order_additional_request: str
  

class BaseQuoteResponse(BaseModel):
  id: str
  user_id: int
  cargo_transportation_id: int
  is_priority: bool
  order_status: OrderStatusEnum
  # order_additional_request: str

class QuoteLocationAccessorialSchema(BaseModel):
  id: Optional[int]
  cargo_accessorial_id: int
  name: str
  

class QuoteLocationSchema(BaseModel):
  id: Optional[int]
  state: str
  county: str
  city: str
  zip_code: str
  address: str
  location_type: LocationTypeEnum
  request_datetime: datetime.datetime
  accessorials: List[QuoteLocationAccessorialSchema]
  

class QuoteCargoSchema(BaseModel):
  id: Optional[int]
  width: int
  length: int
  height: int
  weight: int
  quantity: int
  package_description: str
  cargo_stackable: bool
  cargo_temperature: str
  is_hazardous: bool
  hazardous_detail: str

class CreateQuoteRequest(BaseQuoteRequest):
    from_location: QuoteLocationSchema
    to_location: QuoteLocationSchema
    cargo: List[QuoteCargoSchema]  
    

class UpdateQuoteRequest(BaseQuoteRequest):
    from_location: QuoteLocationSchema  
    to_location: QuoteLocationSchema
    cargo: List[QuoteCargoSchema]

class GetQuoteDetailsResponse(BaseQuoteResponse):
    from_location: QuoteLocationSchema
    to_location: QuoteLocationSchema
    cargo: List[QuoteCargoSchema]
