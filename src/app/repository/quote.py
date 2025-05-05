import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.model._enum import OrderStatusEnum
from app.model.quote import Quote


class QuoteRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_quote(
        self, user_id: int, total_weight: float, total_price: float, quote: Quote
    ):
        quote_id = str(uuid.uuid4().hex.upper())
        quote = Quote(
            id=quote_id,
            user_id=user_id,
            cargo_transportation_id=quote.cargo_transportation_id,
            is_priority=quote.is_priority,
            total_weight=total_weight,
            total_price=total_price,
            order_status=OrderStatusEnum.ESTIMATE,
        )
        self.db_session.add(quote)
        await self.db_session.flush()
        return quote
