import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, join
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional

from app.model._enum import OrderStatusEnum, ShipmentTypeEnum
from app.model.quote import Quote, QuoteLocation, QuoteCargo, QuoteLocationAccessorial


class QuoteRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def get_quotes(self, user_id: int) -> List[Quote]:
        # 한 번의 쿼리로 견적서와 위치 정보를 함께 가져옴
        result = await self.db_session.execute(
            select(Quote)
            .options(selectinload(Quote.quote_location))
            .where(Quote.user_id == user_id)
        )
        quotes = result.scalars().all()
        
        if not quotes:
            return []
        
        # 각 견적서에 위치 정보 설정
        for quote in quotes:
            for location in quote.quote_location:
                location_data = {
                    "id": location.id,
                    "state": location.state,
                    "county": location.county,
                    "city": location.city,
                    "zip_code": location.zip_code,
                    "address": location.address,
                    "request_datetime": location.request_datetime
                }
                
                if location.shipment_type == ShipmentTypeEnum.PICKUP:
                    quote.from_location = location_data
                elif location.shipment_type == ShipmentTypeEnum.DELIVERY:
                    quote.to_location = location_data
        
        return quotes

    async def get_quote_by_id(self, quote_id: str, user_id: int):
        result = await self.db_session.execute(
            select(Quote)
            .options(
                selectinload(Quote.quote_location).selectinload(QuoteLocation.quote_location_accessorial).joinedload(QuoteLocationAccessorial.cargo_accessorial),
                selectinload(Quote.quote_cargo)
            )
            .where(Quote.id == quote_id, Quote.user_id == user_id)
        )
        quote = result.scalar_one_or_none()
        
        if not quote:
            return None
        
        # 위치 정보 설정
        for location in quote.quote_location:
            # 부가 서비스 데이터 변환
            accessorials_data = []
            for acc in location.quote_location_accessorial:
                accessorials_data.append({
                    "cargo_accessorial_id": acc.cargo_accessorial_id,
                    "name": acc.cargo_accessorial.name if acc.cargo_accessorial else ""
                })
            
            location_data = {
                "id": location.id,
                "state": location.state,
                "county": location.county,
                "city": location.city,
                "zip_code": location.zip_code,
                "address": location.address,
                "location_type": location.location_type,
                "request_datetime": location.request_datetime,
                "accessorials": accessorials_data
            }
            
            if location.shipment_type == ShipmentTypeEnum.PICKUP:
                quote.from_location = location_data
            elif location.shipment_type == ShipmentTypeEnum.DELIVERY:
                quote.to_location = location_data
        
        # 화물 정보 설정 - GetQuoteDetailsResponse에서 필요한 cargo 필드
        quote.cargo = quote.quote_cargo
        
        return quote

    async def create_quote(
        self,
        user_id: int,
        total_weight: float,
        base_price: float,
        extra_price: float,
        total_price_with_discount: float,
        quote: Quote,
    ):
        quote_id = str(uuid.uuid4().hex.upper())
        quote = Quote(
            id=quote_id,
            user_id=user_id,
            cargo_transportation_id=quote.cargo_transportation_id,
            is_priority=quote.is_priority,
            total_weight=total_weight,
            base_price=base_price,
            extra_price=extra_price,
            total_price=total_price_with_discount,
            order_status=OrderStatusEnum.ESTIMATE,
        )
        self.db_session.add(quote)
        await self.db_session.flush()
        return quote

    async def update_quote(
        self,
        quote_id: str,
        user_id: int,
        is_priority: bool,
        cargo_transportation_id: int,
        total_weight: float,
        base_price: float,
        extra_price: float,
        total_price_with_discount: float,
    ) -> Quote | None:
        """견적을 업데이트합니다."""
        # 업데이트할 값 준비 - 클라이언트에서 모든 정보를 전달하므로 모든 값 업데이트
        values = {
            "is_priority": is_priority,
            "cargo_transportation_id": cargo_transportation_id,
            "total_weight": total_weight,
            "base_price": base_price,
            "extra_price": extra_price,
            "total_price": total_price_with_discount,
        }

        # 견적 업데이트
        await self.db_session.execute(
            update(Quote)
            .where(Quote.id == quote_id, Quote.user_id == user_id)
            .values(**values)
        )
        await self.db_session.flush()

        # 업데이트된 견적 반환
        return await self.get_quote_by_id(quote_id, user_id)
    
    async def submit_quote(self, quote_id: str, user_id: int):
        await self.db_session.execute(
            update(Quote)
            .where(Quote.id == quote_id, Quote.user_id == user_id)
            .values(order_status=OrderStatusEnum.SUBMIT)
        )
        await self.db_session.flush()