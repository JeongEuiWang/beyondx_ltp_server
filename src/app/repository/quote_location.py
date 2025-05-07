from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional

from app.model.quote import QuoteLocation
from app.model._enum import ShipmentTypeEnum


class QuoteLocationRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_quote_location_by_id(
        self, quote_location_id: int
    ) -> QuoteLocation | None:
        result = await self.db_session.execute(
            select(QuoteLocation).where(QuoteLocation.id == quote_location_id)
        )
        return result.scalar_one_or_none()

    async def get_quote_locations_by_quote_id(
        self, quote_id: str
    ) -> List[QuoteLocation]:
        result = await self.db_session.execute(
            select(QuoteLocation).where(QuoteLocation.quote_id == quote_id)
        )
        return result.scalars().all()

    async def get_quote_location_by_shipment_type(
        self, quote_id: str, shipment_type: ShipmentTypeEnum
    ) -> QuoteLocation | None:
        result = await self.db_session.execute(
            select(QuoteLocation).where(
                QuoteLocation.quote_id == quote_id,
                QuoteLocation.shipment_type == shipment_type,
            )
        )
        return result.scalar_one_or_none()

    async def create_quote_location(
        self,
        quote_id: int,
        quote_location: QuoteLocation,
        shipment_type: ShipmentTypeEnum,
    ) -> QuoteLocation:
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

    async def update_quote_location(
        self, quote_location_id: int, quote_location: dict
    ) -> QuoteLocation:
        values = {
            "state": quote_location.state,
            "county": quote_location.county,
            "city": quote_location.city,
            "zip_code": quote_location.zip_code,
            "address": quote_location.address,
            "location_type": quote_location.location_type,
            "request_datetime": quote_location.request_datetime,
        }

        await self.db_session.execute(
            update(QuoteLocation)
            .where(QuoteLocation.id == quote_location_id)
            .values(**values)
        )
        await self.db_session.flush()

        return await self.get_quote_location_by_id(quote_location_id)
