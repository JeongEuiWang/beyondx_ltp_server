from decimal import Decimal
from typing import List
from ..core.decorator import transactional
from ..core.exceptions import NotFoundException
from ..model._enum import ShipmentTypeEnum
from ..schema._common import BaseQuoteSchema
from ..schema.quote import (
    CreateQuoteRequest,
    UpdateQuoteRequest,
)
from ..repository.quote import QuoteRepository
from ..repository.quote_location import QuoteLocationRepository
from ..repository.quote_location_accessorial import QuoteLocationAccessorialRepository
from ..repository.quote_cargo import QuoteCargoRepository


class QuoteService:
    def __init__(
        self,
        quote_repository: QuoteRepository,
        quote_location_repository: QuoteLocationRepository,
        quote_location_accessorial_repository: QuoteLocationAccessorialRepository,
        quote_cargo_repository: QuoteCargoRepository,
    ):
        self.quote_repository = quote_repository
        self.quote_location_repository = quote_location_repository
        self.quote_location_accessorial_repository = (
            quote_location_accessorial_repository
        )
        self.quote_cargo_repository = quote_cargo_repository
        self.db = None

    async def get_quote_by_id(self, quote_id: str, user_id: int) -> BaseQuoteSchema:
        result = await self.quote_repository.get_quote_by_id(quote_id, user_id)
        if result is None:
            raise NotFoundException(
                message="견적을 찾을 수 없습니다.",
            )
        return BaseQuoteSchema.model_validate(result)

    @transactional()
    async def create_quote(
        self,
        user_id: int,
        quote: CreateQuoteRequest,
        total_weight: Decimal,
        base_price: Decimal,
        extra_price: Decimal,
        total_price_with_discount: Decimal,
    ) -> BaseQuoteSchema:
        new_quote = await self.quote_repository.create_quote(
            user_id=user_id,
            total_weight=total_weight,
            base_price=base_price,
            extra_price=extra_price,
            total_price_with_discount=total_price_with_discount,
            quote=quote,
        )
        new_from_location = await self.quote_location_repository.create_quote_location(
            new_quote.id, quote.from_location, ShipmentTypeEnum.PICKUP
        )
        await self.quote_location_accessorial_repository.create_quote_location_accessorial(
            new_from_location.id, quote.from_location.accessorials
        )
        new_to_location = await self.quote_location_repository.create_quote_location(
            new_quote.id, quote.to_location, ShipmentTypeEnum.DELIVERY
        )
        await self.quote_location_accessorial_repository.create_quote_location_accessorial(
            new_to_location.id, quote.to_location.accessorials
        )
        await self.quote_cargo_repository.create_quote_cargo(new_quote.id, quote.cargo)

        return BaseQuoteSchema.model_validate(new_quote)

    @transactional()
    async def update_quote(
        self,
        quote_id: str,
        user_id: int,
        quote: UpdateQuoteRequest,
        total_weight: Decimal,
        base_price: Decimal,
        extra_price: Decimal,
        total_price_with_discount: Decimal,
    ) -> BaseQuoteSchema:
        updated_quote = await self.quote_repository.update_quote(
            quote_id=quote_id,
            user_id=user_id,
            is_priority=quote.is_priority,
            cargo_transportation_id=quote.cargo_transportation_id,
            total_weight=total_weight,
            base_price=base_price,
            extra_price=extra_price,
            total_price_with_discount=total_price_with_discount,
        )

        # 출발지 정보 업데이트 - 전체 정보를 전달받으므로 그대로 업데이트
        from_location = (
            await self.quote_location_repository.get_quote_location_by_shipment_type(
                quote_id, ShipmentTypeEnum.PICKUP
            )
        )
        if from_location is None:
            raise NotFoundException(
                message="출발지 정보를 찾을 수 없습니다.",
            )
        await self.quote_location_repository.update_quote_location(
            from_location.id, quote.from_location
        )

        await self._update_accessorials(
            from_location.id, quote.from_location.accessorials
        )

        # 도착지 정보 업데이트 - 전체 정보를 전달받으므로 그대로 업데이트
        to_location = (
            await self.quote_location_repository.get_quote_location_by_shipment_type(
                quote_id, ShipmentTypeEnum.DELIVERY
            )
        )
        if to_location is None:
            raise NotFoundException(
                message="도착지 정보를 찾을 수 없습니다.",
            )

        await self.quote_location_repository.update_quote_location(
            to_location.id, quote.to_location
        )

        await self._update_accessorials(to_location.id, quote.to_location.accessorials)

        await self.quote_cargo_repository.delete_quote_cargo(quote_id)
        await self.quote_cargo_repository.create_quote_cargo(quote_id, quote.cargo)

        return BaseQuoteSchema.model_validate(updated_quote)

    async def _update_accessorials(self, location_id: int, new_accessorials: List):
        current_accessorials = await self.quote_location_accessorial_repository.get_quote_location_accessorials(
            location_id
        )
        current_cargo_accessorial_ids = {
            acc.cargo_accessorial_id for acc in current_accessorials
        }

        new_cargo_accessorial_ids = {
            acc.cargo_accessorial_id for acc in new_accessorials
        }

        to_delete = current_cargo_accessorial_ids - new_cargo_accessorial_ids
        to_add = [
            acc
            for acc in new_accessorials
            if acc.cargo_accessorial_id
            in (new_cargo_accessorial_ids - current_cargo_accessorial_ids)
        ]

        # 4. 데이터베이스에 변경 사항 적용
        if to_delete:
            await self.quote_location_accessorial_repository.delete_specific_accessorials(
                location_id, list(to_delete)
            )

        if to_add:
            await self.quote_location_accessorial_repository.create_quote_location_accessorial(
                location_id, to_add
            )
