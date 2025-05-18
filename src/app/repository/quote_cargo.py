from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from app.model.quote import QuoteCargo


class QuoteCargoRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_quote_cargo(
        self, quote_id: int, quote_cargo: List[QuoteCargo]
    ) -> List[QuoteCargo]:
        quote_cargos = [
            QuoteCargo(
                quote_id=quote_id,
                width=cargo.width,
                length=cargo.length,
                height=cargo.height,
                weight=cargo.weight,
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

    async def get_quote_cargo(self, quote_id: str) -> List[QuoteCargo]:
        result = await self.db_session.execute(
            select(QuoteCargo).where(QuoteCargo.quote_id == quote_id)
        )
        return result.scalars().all()

    async def delete_quote_cargo(self, quote_id: str):
        """견적 ID에 해당하는 모든 화물 정보를 삭제합니다."""
        await self.db_session.execute(
            delete(QuoteCargo).where(QuoteCargo.quote_id == quote_id)
        )
        await self.db_session.flush()
