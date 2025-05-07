from typing import List
from app.schema._common import QuoteLocationSchema, QuoteCargoSchema
from app.schema._base import BaseSchema


class CreateQuoteRequest(BaseSchema):
    cargo_transportation_id: int
    is_priority: bool
    from_location: QuoteLocationSchema
    to_location: QuoteLocationSchema
    cargo: List[QuoteCargoSchema]


class UpdateQuoteRequest(BaseSchema):
    cargo_transportation_id: int
    is_priority: bool
    from_location: QuoteLocationSchema
    to_location: QuoteLocationSchema
    cargo: List[QuoteCargoSchema]
