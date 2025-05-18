from datetime import datetime
from typing import List
from ...schema._common import BaseQuoteSchema, QuoteLocationSchema, QuoteCargoSchema
from ...schema._base import BaseSchema, IntegerIDSchema, StringIDSchema


class QuoteLocationWithIDSchema(IntegerIDSchema, QuoteLocationSchema):
    pass


class QuoteCargoWithIDSchema(IntegerIDSchema, QuoteCargoSchema):
    pass


class GetQuoteDetailsResponse(BaseQuoteSchema):
    from_location: QuoteLocationWithIDSchema
    to_location: QuoteLocationWithIDSchema
    cargo: List[QuoteCargoWithIDSchema]

class GetQuotesLocationSchema(IntegerIDSchema, BaseSchema):
    state: str
    county: str
    city: str
    zip_code: str
    address: str
    request_datetime: datetime

class GetQuotesResponse(BaseQuoteSchema):
    from_location: GetQuotesLocationSchema
    to_location: GetQuotesLocationSchema
