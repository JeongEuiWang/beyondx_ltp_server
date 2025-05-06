import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.model._enum import LocationTypeEnum

class BaseQuoteRequest(BaseModel):
  cargo_transportation_id: int
  is_priority: bool
  # order_additional_request: str

class QuoteLocationAccessorialRequest(BaseModel):
  cargo_accessorial_id: int
  name: str
  

class QuoteLocationRequest(BaseModel):
  state: str
  county: str
  city: str
  zip_code: str
  address: str
  location_type: LocationTypeEnum
  request_datetime: datetime.datetime
  accessorials: List[QuoteLocationAccessorialRequest]
  

class QuoteCargoRequest(BaseModel):
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
    from_location: QuoteLocationRequest
    to_location: QuoteLocationRequest
    cargo: List[QuoteCargoRequest]  
    

class UpdateQuoteRequest(BaseQuoteRequest):
    from_location: QuoteLocationRequest
    to_location: QuoteLocationRequest
    cargo: List[QuoteCargoRequest]