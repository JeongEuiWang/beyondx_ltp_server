import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, join, func, cast, Date
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from datetime import date

from app.model._enum import OrderStatusEnum, ShipmentTypeEnum
from app.model.quote import Quote, QuoteLocation, QuoteCargo, QuoteLocationAccessorial
from ..schema.quote.request import CreateQuoteRequest


class QuoteRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_all_quotes(self, status: List[str]) -> List[Quote]:
        result = await self.db_session.execute(
            select(Quote)
            .options(
                selectinload(Quote.quote_location), selectinload(Quote.quote_cargo)
            )
            .where(Quote.order_status.in_(status))
        )
        quotes = result.scalars().unique().all()
        return quotes

    async def get_quotes(self, user_id: int) -> List[Quote]:
        result = await self.db_session.execute(
            select(Quote)
            .options(
                selectinload(Quote.quote_location), selectinload(Quote.quote_cargo)
            )
            .where(Quote.user_id == user_id)
        )
        quotes = result.scalars().unique().all()

        return quotes

    async def get_quote_by_id(self, quote_id: str) -> Optional[Quote]:
        result = await self.db_session.execute(
            select(Quote)
            .options(
                selectinload(Quote.quote_location)
                .selectinload(QuoteLocation.quote_location_accessorial)
                .joinedload(QuoteLocationAccessorial.cargo_accessorial),
                selectinload(Quote.quote_cargo),
            )
            .where(Quote.id == quote_id)
        )
        quote = result.scalar_one_or_none()

        return quote

    async def create_quote(
        self,
        user_id: int,
        total_weight: float,
        base_price: float,
        extra_price: float,
        total_price_with_discount: float,
        quote_payload: CreateQuoteRequest,
    ) -> Quote:
        quote_id = str(uuid.uuid4().hex.upper())
        new_quote = Quote(
            id=quote_id,
            user_id=user_id,
            cargo_transportation_id=quote_payload.cargo_transportation_id,
            is_priority=quote_payload.is_priority,
            total_weight=total_weight,
            base_price=base_price,
            extra_price=extra_price,
            total_price=total_price_with_discount,
            order_status=OrderStatusEnum.ESTIMATE,
        )
        self.db_session.add(new_quote)
        await self.db_session.flush()
        return new_quote

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
        values = {
            "is_priority": is_priority,
            "cargo_transportation_id": cargo_transportation_id,
            "total_weight": total_weight,
            "base_price": base_price,
            "extra_price": extra_price,
            "total_price": total_price_with_discount,
        }

        await self.db_session.execute(
            update(Quote)
            .where(Quote.id == quote_id, Quote.user_id == user_id)
            .values(**values)
        )
        await self.db_session.flush()

        return await self.get_quote_by_id(quote_id)

    async def get_user_submit_count(self, user_id: int, target_date: date) -> int:
        result = await self.db_session.execute(
            select(func.count(Quote.id)).where(
                Quote.user_id == user_id,
                Quote.order_status == OrderStatusEnum.SUBMIT,
            )
        )
        return result.scalar() or 0

    async def submit_quote(self, quote_id: str, user_id: int, order_primary: str):
        await self.db_session.execute(
            update(Quote)
            .where(Quote.id == quote_id, Quote.user_id == user_id)
            .values(order_status=OrderStatusEnum.SUBMIT, order_primary=order_primary)
        )
        await self.db_session.flush()

    async def confirm_quote(self, quote_id: str, actual_price: float):
        await self.db_session.execute(
            update(Quote)
            .where(Quote.id == quote_id)
            .values(order_status=OrderStatusEnum.ACCEPT, total_price=actual_price)
        )
        await self.db_session.flush()
