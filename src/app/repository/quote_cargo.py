from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.model.quote import QuoteCargo


class QuoteCargoRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_quote_cargo(self, quote_id: int, quote_cargo: List[QuoteCargo] ):
        quote_cargos = [
            QuoteCargo(
                quote_id=quote_id,
                width=cargo.width,
                length=cargo.length,
                height=cargo.height,
                quantity=cargo.quantity,
                package_description=cargo.package_description,
                cargo_stackable=cargo.cargo_stackable,
                cargo_temperature=cargo.cargo_temperature,
                is_hazardous=cargo.is_hazardous,
                hazardous_detail=cargo.hazardous_detail,
            )
            for cargo in quote_cargo
        ]
        self.db_session.add_all(quote_cargos)
        await self.db_session.flush()
        return quote_cargos
