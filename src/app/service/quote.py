from decimal import Decimal
from app.core.decorator import transactional
from app.model._enum import ShipmentTypeEnum
from ..schema.quote import CreateQuoteRequest
from ..repository.quote import QuoteRepository
from ..repository.quote_location import QuoteLocationRepository
from ..repository.quote_cargo import QuoteCargoRepository


class QuoteService:
    def __init__(
        self,
        quote_repository: QuoteRepository,
        quote_location_repository: QuoteLocationRepository,
        quote_cargo_repository: QuoteCargoRepository,
    ):
        self.quote_repository = quote_repository
        self.quote_location_repository = quote_location_repository
        self.quote_cargo_repository = quote_cargo_repository
        self.db = None

    @transactional()
    async def create_quote(
        self,
        user_id: int,
        quote: CreateQuoteRequest,
        total_weight: Decimal,
        total_cost: Decimal,
    ):
        new_quote = await self.quote_repository.create_quote(
            user_id=user_id,
            total_weight=total_weight,
            total_price=total_cost,
            quote=quote,
        )
        new_from_location = await self.quote_location_repository.create_quote_location(
            new_quote.id, quote.from_location, ShipmentTypeEnum.PICKUP
        )
        await self.quote_location_repository.create_quote_location_accessorial(
            new_from_location.id, quote.from_location.accessorials
        )
        new_to_location = await self.quote_location_repository.create_quote_location(
            new_quote.id, quote.to_location, ShipmentTypeEnum.DELIVERY
        )
        await self.quote_location_repository.create_quote_location_accessorial(
            new_to_location.id, quote.to_location.accessorials
        )
        await self.quote_cargo_repository.create_quote_cargo(new_quote.id, quote.cargo)

        return new_quote
