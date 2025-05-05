from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.model.quote import QuoteLocation, QuoteLocationAccessorial
from app.model._enum import ShipmentTypeEnum

class QuoteLocationRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_quote_location(self, quote_id: int, quote_location: QuoteLocation, shipment_type: ShipmentTypeEnum):
        quote_location = QuoteLocation(
            quote_id=quote_id,
            state=quote_location.state,
            county=quote_location.county,
            city=quote_location.city,
            zip_code=quote_location.zip_code,
            address=quote_location.address,
            location_type=quote_location.location_type,
            shipment_type=shipment_type,
            request_datetime=quote_location.request_datetime,
        )
        self.db_session.add(quote_location)
        await self.db_session.flush()
        return quote_location
    
    async def create_quote_location_accessorial(self, quote_location_id: int, quote_location_accessorial: List[QuoteLocationAccessorial]):
        quote_location_accessorials = [
            QuoteLocationAccessorial(
                quote_location_id=quote_location_id,
                cargo_accessorial_id=accessorial.cargo_accessorial_id,
            )
            for accessorial in quote_location_accessorial
        ]
        self.db_session.add_all(quote_location_accessorials)
        await self.db_session.flush()
