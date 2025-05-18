from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload
from typing import List, Set

from app.model.quote import QuoteLocationAccessorial
from ..schema._common import QuoteLocationAccessorialSchema


class QuoteLocationAccessorialRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_quote_location_accessorial_by_id(
        self, quote_location_accessorial_id: int
    ) -> QuoteLocationAccessorial | None:
        result = await self.db_session.execute(
            select(QuoteLocationAccessorial).where(
                QuoteLocationAccessorial.id == quote_location_accessorial_id
            )
        )
        return result.scalars_one_or_none()

    async def get_quote_location_accessorials(
        self, quote_location_id: int
    ) -> List[QuoteLocationAccessorial]:
        """특정 인용 위치의 부가 서비스 목록을 조회합니다."""
        result = await self.db_session.execute(
            select(QuoteLocationAccessorial)
            .options(joinedload(QuoteLocationAccessorial.cargo_accessorial))
            .where(QuoteLocationAccessorial.quote_location_id == quote_location_id)
        )
        return result.scalars().all()

    async def create_quote_location_accessorial(
        self,
        quote_location_id: int,
        accessorial_schemas: List[QuoteLocationAccessorialSchema],
    ) -> List[QuoteLocationAccessorial]:
        """인용 위치 부가 서비스를 생성합니다."""
        new_accessorial_models = [
            QuoteLocationAccessorial(
                quote_location_id=quote_location_id,
                cargo_accessorial_id=schema.cargo_accessorial_id,
            )
            for schema in accessorial_schemas
        ]
        self.db_session.add_all(new_accessorial_models)
        await self.db_session.flush()
        return new_accessorial_models
      
    async def delete_quote_location_accessorial(self, quote_location_id: int):
        """인용 위치 부가 서비스를 모두 삭제합니다."""
        await self.db_session.execute(
            delete(QuoteLocationAccessorial).where(
                QuoteLocationAccessorial.quote_location_id == quote_location_id
            )
        )
        await self.db_session.flush()

    async def delete_specific_accessorials(
        self, quote_location_id: int, cargo_accessorial_ids: List[int]
    ):
        """특정 인용 위치에서 지정된 부가 서비스만 삭제합니다."""
        if not cargo_accessorial_ids:
            return

        await self.db_session.execute(
            delete(QuoteLocationAccessorial).where(
                QuoteLocationAccessorial.quote_location_id == quote_location_id,
                QuoteLocationAccessorial.cargo_accessorial_id.in_(
                    cargo_accessorial_ids
                ),
            )
        )
        await self.db_session.flush()
