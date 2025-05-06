from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional

from app.model.quote import QuoteLocation
from app.model._enum import ShipmentTypeEnum


class QuoteLocationRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_quote_locations_by_quote_id(self, quote_id: str) -> List[QuoteLocation]:
        result = await self.db_session.execute(
            select(QuoteLocation).where(QuoteLocation.quote_id == quote_id)
        )
        return result.scalars().all()

    async def get_quote_location_by_shipment_type(
        self, quote_id: str, shipment_type: ShipmentTypeEnum
    ) -> Optional[QuoteLocation]:
        result = await self.db_session.execute(
            select(QuoteLocation).where(
                QuoteLocation.quote_id == quote_id,
                QuoteLocation.shipment_type == shipment_type,
            )
        )
        return result.scalars().first()

    async def create_quote_location(
        self,
        quote_id: int,
        quote_location: QuoteLocation,
        shipment_type: ShipmentTypeEnum,
    ):
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
    ) -> Optional[QuoteLocation]:
        """인용 위치를 업데이트합니다."""
        # 업데이트할 값 준비 - 클라이언트에서 모든 정보를 전달하므로 모든 필드 업데이트
        values = {
            "state": quote_location.state,
            "county": quote_location.county,
            "city": quote_location.city,
            "zip_code": quote_location.zip_code,
            "address": quote_location.address,
            "location_type": quote_location.location_type,
            "request_datetime": quote_location.request_datetime,
        }

        # 인용 위치 업데이트
        await self.db_session.execute(
            update(QuoteLocation)
            .where(QuoteLocation.id == quote_location_id)
            .values(**values)
        )
        await self.db_session.flush()

        # 업데이트된 인용 위치 반환
        result = await self.db_session.execute(
            select(QuoteLocation).where(QuoteLocation.id == quote_location_id)
        )
        return result.scalars().first()
