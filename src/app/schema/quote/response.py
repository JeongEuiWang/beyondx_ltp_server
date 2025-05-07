from typing import List
from ...schema._common import QuoteLocationSchema, QuoteCargoSchema
from ...schema._base import BaseSchema, IntegerIDSchema, StringIDSchema

class QuoteLocationWithIDSchema(IntegerIDSchema, QuoteLocationSchema):
    pass

class QuoteCargoWithIDSchema(IntegerIDSchema, QuoteCargoSchema):
    pass  


class GetQuoteDetailsResponse(StringIDSchema, BaseSchema):
    from_location: QuoteLocationWithIDSchema
    to_location: QuoteLocationWithIDSchema
    cargo: List[QuoteCargoWithIDSchema]