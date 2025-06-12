from decimal import Decimal
from pprint import pprint
from typing import List, Optional
from datetime import datetime, date
import calendar

from fastapi import HTTPException, Depends
from app.core.auth import TokenData, required_authorization

from app.service.bol import create_structured_bill_of_lading
import os
from ..db.unit_of_work import UnitOfWork
from ..model.quote import Quote
from ..model.quote import QuoteLocation
from ..model.quote import QuoteCargo
from ..core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from ..model._enum import ShipmentTypeEnum, OrderStatusEnum
from ..schema._common import BaseQuoteSchema, QuoteLocationAccessorialSchema
from ..schema.quote.request import (
    CreateQuoteRequest,
    UpdateQuoteRequest,
    ConfirmQuoteRequest,
)
from ..schema.quote.response import (
    GetQuotesResponse,
    GetQuoteDetailsResponse,
    QuoteLocationWithIDSchema,
    QuoteCargoWithIDSchema,
    GetQuotesLocationSchema,
)
from app.service.email import EmailSender


class QuoteService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def get_quotes_admin(
        self, role_id: int, status: List[str]
    ) -> List[GetQuotesResponse]:
        async with self.uow:
            if role_id != 2:
                raise ForbiddenException(message="Forbidden:: Admin only")

            quote_models = await self.uow.quote.get_all_quotes(status)
            response_list = []
            for quote_model in quote_models:
                from_location_data = None
                to_location_data = None
                for loc_model in quote_model.quote_location:
                    loc_schema_data = GetQuotesLocationSchema.model_validate(loc_model)
                    if loc_model.shipment_type == ShipmentTypeEnum.PICKUP:
                        from_location_data = loc_schema_data
                    elif loc_model.shipment_type == ShipmentTypeEnum.DELIVERY:
                        to_location_data = loc_schema_data

                if not from_location_data or not to_location_data:
                    continue

                cargo_data = []
                if hasattr(quote_model, "quote_cargo") and quote_model.quote_cargo:
                    cargo_data = [
                        QuoteCargoWithIDSchema.model_validate(qc_model)
                        for qc_model in quote_model.quote_cargo
                    ]

                response_list.append(
                    GetQuotesResponse(
                        id=quote_model.id,
                        user_id=quote_model.user_id,
                        cargo_transportation_id=quote_model.cargo_transportation_id,
                        is_priority=quote_model.is_priority,
                        total_weight=quote_model.total_weight,
                        base_price=quote_model.base_price,
                        extra_price=quote_model.extra_price,
                        total_price=quote_model.total_price,
                        order_status=quote_model.order_status,
                        order_primary=quote_model.order_primary,
                        order_additional_request=quote_model.order_additional_request,
                        from_location=from_location_data,
                        to_location=to_location_data,
                        cargo=cargo_data,
                        created_at=quote_model.created_at,
                    )
                )
            return sorted(response_list, key=lambda x: x.created_at, reverse=True)

    async def get_quotes(self, user_id: int) -> List[GetQuotesResponse]:
        async with self.uow:
            quote_models = await self.uow.quote.get_quotes(user_id)
            response_list = []
            for quote_model in quote_models:
                from_location_data = None
                to_location_data = None
                for loc_model in quote_model.quote_location:
                    loc_schema_data = GetQuotesLocationSchema.model_validate(loc_model)
                    if loc_model.shipment_type == ShipmentTypeEnum.PICKUP:
                        from_location_data = loc_schema_data
                    elif loc_model.shipment_type == ShipmentTypeEnum.DELIVERY:
                        to_location_data = loc_schema_data

                if not from_location_data or not to_location_data:
                    continue

                cargo_data = []
                if hasattr(quote_model, "quote_cargo") and quote_model.quote_cargo:
                    cargo_data = [
                        QuoteCargoWithIDSchema.model_validate(qc_model)
                        for qc_model in quote_model.quote_cargo
                    ]

                response_list.append(
                    GetQuotesResponse(
                        id=quote_model.id,
                        user_id=quote_model.user_id,
                        cargo_transportation_id=quote_model.cargo_transportation_id,
                        is_priority=quote_model.is_priority,
                        total_weight=quote_model.total_weight,
                        base_price=quote_model.base_price,
                        extra_price=quote_model.extra_price,
                        total_price=quote_model.total_price,
                        order_status=quote_model.order_status,
                        order_primary=quote_model.order_primary,
                        order_additional_request=quote_model.order_additional_request,
                        from_location=from_location_data,
                        to_location=to_location_data,
                        cargo=cargo_data,
                        created_at=quote_model.created_at,
                    )
                )
            return sorted(response_list, key=lambda x: x.created_at, reverse=True)

    async def _get_location_detail_schema(
        self, loc_model: QuoteLocation
    ) -> QuoteLocationWithIDSchema:
        accessorial_models = (
            await self.uow.quote_location_accessorial.get_quote_location_accessorials(
                loc_model.id
            )
        )
        accessorial_schemas = [
            QuoteLocationAccessorialSchema(
                cargo_accessorial_id=acc.cargo_accessorial_id,
                name=acc.cargo_accessorial.name,
            )
            for acc in accessorial_models
        ]
        return QuoteLocationWithIDSchema(
            id=loc_model.id,
            state=loc_model.state,
            county=loc_model.county,
            city=loc_model.city,
            zip_code=loc_model.zip_code,
            address=loc_model.address,
            location_type=loc_model.location_type,
            request_datetime=loc_model.request_datetime,
            accessorials=accessorial_schemas,
        )

    async def _get_cargo_detail_schemas(
        self, quote_cargo_models: List[QuoteCargo]
    ) -> List[QuoteCargoWithIDSchema]:
        return [
            QuoteCargoWithIDSchema.model_validate(qc_model)
            for qc_model in quote_cargo_models
        ]

    async def get_quote_by_id(
        self, quote_id: str, token_data: TokenData
    ) -> GetQuoteDetailsResponse:
        async with self.uow:

            quote_model = await self.uow.quote.get_quote_by_id(quote_id)

            if token_data.role_id == 1 and quote_model.user_id != token_data.user_id:
                raise ForbiddenException(message="Forbidden:: Owner only")

            pprint(quote_model.__dict__ if quote_model else "quote_model is None")
            if quote_model:
                quote_location_models = quote_model.quote_location
                if quote_location_models and len(quote_location_models) > 0:
                    pprint(
                        quote_location_models[0].__dict__
                        if len(quote_location_models) > 0
                        else "quote_location_models[0] is not accessible"
                    )
                    if len(quote_location_models) > 1:
                        pprint(
                            quote_location_models[1].__dict__
                            if len(quote_location_models) > 1
                            else "quote_location_models[1] is not accessible"
                        )
                else:
                    print("quote_location_models is None or empty")

                quote_cargo_models = quote_model.quote_cargo
                if quote_cargo_models and len(quote_cargo_models) > 0:
                    pprint(
                        quote_cargo_models[0].__dict__
                        if len(quote_cargo_models) > 0
                        else "quote_cargo_models[0] is not accessible"
                    )
                else:
                    print("quote_cargo_models is None or empty")

            if quote_model is None:
                raise NotFoundException(message="견적을 찾을 수 없습니다.")

            from_location_detail = None
            to_location_detail = None

            if hasattr(quote_model, "quote_location") and quote_model.quote_location:
                for loc_model in quote_model.quote_location:
                    loc_detail_schema = await self._get_location_detail_schema(
                        loc_model
                    )
                    if loc_model.shipment_type == ShipmentTypeEnum.PICKUP:
                        from_location_detail = loc_detail_schema
                    elif loc_model.shipment_type == ShipmentTypeEnum.DELIVERY:
                        to_location_detail = loc_detail_schema

            if not from_location_detail or not to_location_detail:
                raise NotFoundException(
                    message=f"견적 {quote_id}의 출발지 또는 도착지 정보를 찾을 수 없습니다."
                )

            cargo_details = []
            if hasattr(quote_model, "quote_cargo") and quote_model.quote_cargo:
                cargo_details = await self._get_cargo_detail_schemas(
                    quote_model.quote_cargo
                )

            return GetQuoteDetailsResponse(
                id=quote_model.id,
                user_id=quote_model.user_id,
                cargo_transportation_id=quote_model.cargo_transportation_id,
                is_priority=quote_model.is_priority,
                total_weight=quote_model.total_weight,
                base_price=quote_model.base_price,
                extra_price=quote_model.extra_price,
                total_price=quote_model.total_price,
                order_status=quote_model.order_status,
                order_primary=quote_model.order_primary,
                order_additional_request=quote_model.order_additional_request,
                from_location=from_location_detail,
                to_location=to_location_detail,
                cargo=cargo_details,
                created_at=quote_model.created_at,
            )

    async def create_quote(
        self,
        user_id: int,
        quote_data: CreateQuoteRequest,
        total_weight: Decimal,
        base_price: Decimal,
        extra_price: Decimal,
        total_price_with_discount: Decimal,
    ) -> BaseQuoteSchema:
        async with self.uow:
            new_quote_model = await self.uow.quote.create_quote(
                user_id=user_id,
                total_weight=total_weight,
                base_price=base_price,
                extra_price=extra_price,
                total_price_with_discount=total_price_with_discount,
                quote_payload=quote_data,
            )

            await self.uow.quote_location.create_quote_location(
                new_quote_model.id, quote_data.from_location, ShipmentTypeEnum.PICKUP
            )
            await self.uow.quote_location_accessorial.create_quote_location_accessorial(
                (
                    await self.uow.quote_location.get_quote_location_by_shipment_type(
                        new_quote_model.id, ShipmentTypeEnum.PICKUP
                    )
                ).id,
                quote_data.from_location.accessorials,
            )
            await self.uow.quote_location.create_quote_location(
                new_quote_model.id, quote_data.to_location, ShipmentTypeEnum.DELIVERY
            )
            await self.uow.quote_location_accessorial.create_quote_location_accessorial(
                (
                    await self.uow.quote_location.get_quote_location_by_shipment_type(
                        new_quote_model.id, ShipmentTypeEnum.DELIVERY
                    )
                ).id,
                quote_data.to_location.accessorials,
            )
            await self.uow.quote_cargo.create_quote_cargo(
                new_quote_model.id, quote_data.cargo
            )

            return BaseQuoteSchema.model_validate(new_quote_model)

    async def update_quote(
        self,
        quote_id: str,
        user_id: int,
        quote_data: UpdateQuoteRequest,
        total_weight: Decimal,
        base_price: Decimal,
        extra_price: Decimal,
        total_price_with_discount: Decimal,
    ) -> GetQuoteDetailsResponse:
        async with self.uow:
            updated_quote_model = await self.uow.quote.update_quote(
                quote_id=quote_id,
                user_id=user_id,
                is_priority=quote_data.is_priority,
                cargo_transportation_id=quote_data.cargo_transportation_id,
                total_weight=total_weight,
                base_price=base_price,
                extra_price=extra_price,
                total_price_with_discount=total_price_with_discount,
            )
            if updated_quote_model is None:
                raise NotFoundException(
                    message=f"견적 ID {quote_id}를 업데이트하거나 찾을 수 없습니다."
                )

            from_location_model = (
                await self.uow.quote_location.get_quote_location_by_shipment_type(
                    quote_id, ShipmentTypeEnum.PICKUP
                )
            )
            if from_location_model is None:
                raise NotFoundException(
                    message=f"견적 {quote_id}의 출발지 정보를 찾을 수 없습니다."
                )
            await self.uow.quote_location.update_quote_location(
                from_location_model.id, quote_data.from_location
            )
            await self._update_accessorials(
                from_location_model.id, quote_data.from_location.accessorials
            )

            to_location_model = (
                await self.uow.quote_location.get_quote_location_by_shipment_type(
                    quote_id, ShipmentTypeEnum.DELIVERY
                )
            )
            if to_location_model is None:
                raise NotFoundException(
                    message=f"견적 {quote_id}의 도착지 정보를 찾을 수 없습니다."
                )
            await self.uow.quote_location.update_quote_location(
                to_location_model.id, quote_data.to_location
            )
            await self._update_accessorials(
                to_location_model.id, quote_data.to_location.accessorials
            )

            await self.uow.quote_cargo.delete_quote_cargo(quote_id)
            created_cargos_models = await self.uow.quote_cargo.create_quote_cargo(
                quote_id, quote_data.cargo
            )

            from_accessorial_models = await self.uow.quote_location_accessorial.get_quote_location_accessorials(
                from_location_model.id
            )
            from_accessorial_schemas = [
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=acc.cargo_accessorial_id,
                    name=acc.cargo_accessorial.name,
                )
                for acc in from_accessorial_models
            ]

            from_location_schema = QuoteLocationWithIDSchema(
                id=from_location_model.id,
                state=from_location_model.state,
                county=from_location_model.county,
                city=from_location_model.city,
                zip_code=from_location_model.zip_code,
                address=from_location_model.address,
                location_type=from_location_model.location_type,
                request_datetime=from_location_model.request_datetime,
                accessorials=from_accessorial_schemas,
            )

            to_accessorial_models = await self.uow.quote_location_accessorial.get_quote_location_accessorials(
                to_location_model.id
            )
            to_accessorial_schemas = [
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=acc.cargo_accessorial_id,
                    name=acc.cargo_accessorial.name,
                )
                for acc in to_accessorial_models
            ]

            to_location_schema = QuoteLocationWithIDSchema(
                id=to_location_model.id,
                state=to_location_model.state,
                county=to_location_model.county,
                city=to_location_model.city,
                zip_code=to_location_model.zip_code,
                address=to_location_model.address,
                location_type=to_location_model.location_type,
                request_datetime=to_location_model.request_datetime,
                accessorials=to_accessorial_schemas,
            )

            cargo_details_schemas = []
            for qc_model in created_cargos_models:
                cargo_details_schemas.append(
                    QuoteCargoWithIDSchema.model_validate(qc_model)
                )

            return GetQuoteDetailsResponse(
                id=updated_quote_model.id,
                user_id=updated_quote_model.user_id,
                cargo_transportation_id=updated_quote_model.cargo_transportation_id,
                is_priority=updated_quote_model.is_priority,
                total_weight=updated_quote_model.total_weight,
                base_price=updated_quote_model.base_price,
                extra_price=updated_quote_model.extra_price,
                total_price=updated_quote_model.total_price,
                order_status=updated_quote_model.order_status,
                order_primary=updated_quote_model.order_primary,
                order_additional_request=updated_quote_model.order_additional_request,
                from_location=from_location_schema,
                to_location=to_location_schema,
                cargo=cargo_details_schemas,
                created_at=updated_quote_model.created_at,
            )

    async def _update_accessorials(
        self, location_id: int, new_accessorials: List[QuoteLocationAccessorialSchema]
    ):
        current_accessorials = (
            await self.uow.quote_location_accessorial.get_quote_location_accessorials(
                location_id
            )
        )
        current_cargo_accessorial_ids = {
            acc.cargo_accessorial_id for acc in current_accessorials
        }
        new_cargo_accessorial_ids = {
            acc_schema.cargo_accessorial_id for acc_schema in new_accessorials
        }

        to_delete_ids = current_cargo_accessorial_ids - new_cargo_accessorial_ids

        to_add_schemas = [
            acc_schema
            for acc_schema in new_accessorials
            if acc_schema.cargo_accessorial_id
            in (new_cargo_accessorial_ids - current_cargo_accessorial_ids)
        ]

        if to_delete_ids:
            await self.uow.quote_location_accessorial.delete_specific_accessorials(
                location_id, list(to_delete_ids)
            )
        if to_add_schemas:
            await self.uow.quote_location_accessorial.create_quote_location_accessorial(
                location_id, to_add_schemas
            )

    async def _prepare_bol_payload(self, quote_model: Quote) -> dict:

        from_loc_bol_schema = None
        to_loc_bol_schema = None

        if hasattr(quote_model, "quote_location") and quote_model.quote_location:
            for loc_model in quote_model.quote_location:
                loc_schema = await self._get_location_detail_schema(loc_model)
                if loc_model.shipment_type == ShipmentTypeEnum.PICKUP:
                    from_loc_bol_schema = loc_schema
                elif loc_model.shipment_type == ShipmentTypeEnum.DELIVERY:
                    to_loc_bol_schema = loc_schema

        if not from_loc_bol_schema or not to_loc_bol_schema:
            raise NotFoundException(
                message=f"견적 {quote_model.id}의 BOL 생성을 위한 위치 정보를 찾을 수 없습니다."
            )

        cargo_bol_schemas = []
        if hasattr(quote_model, "quote_cargo") and quote_model.quote_cargo:
            cargo_bol_schemas = await self._get_cargo_detail_schemas(
                quote_model.quote_cargo
            )

        quote_data_for_bol_dict = {
            "id": quote_model.id,
            "user_id": quote_model.user_id,
            "cargo_transportation_id": quote_model.cargo_transportation_id,
            "is_priority": quote_model.is_priority,
            "total_weight": quote_model.total_weight,
            "base_price": quote_model.base_price,
            "extra_price": quote_model.extra_price,
            "total_price": quote_model.total_price,
            "order_status": quote_model.order_status.value,
            "order_primary": quote_model.order_primary,
            "order_additional_request": quote_model.order_additional_request,
            "from_location": (
                from_loc_bol_schema.model_dump() if from_loc_bol_schema else None
            ),
            "to_location": (
                to_loc_bol_schema.model_dump() if to_loc_bol_schema else None
            ),
            "cargo": [c.model_dump() for c in cargo_bol_schemas],
        }
        return quote_data_for_bol_dict

    def _generate_customer_code(self, user_id: int) -> str:
        prefix_index = (user_id - 1) // 99  # 0부터 시작
        suffix_number = ((user_id - 1) % 99) + 1  # 1-99 범위

        prefix_char = chr(ord("A") + prefix_index)

        return f"{prefix_char}{suffix_number:02d}"

    def _generate_order_primary(self, user_id: int, daily_count: int) -> str:
        now = datetime.now()

        year = now.year % 100
        if year < 25:
            year += 100

        week = now.isocalendar()[1]

        day_of_week = now.isoweekday()

        customer_code = self._generate_customer_code(user_id)

        order_count = daily_count + 1

        return f"{year:02d}{week:02d}{day_of_week}{customer_code}{order_count:02d}"

    async def submit_quote(
        self, quote_id: str, user_id: int, token_data: TokenData
    ) -> GetQuoteDetailsResponse:
        async with self.uow:
            today = date.today()
            daily_submit_count = await self.uow.quote.get_user_submit_count(
                user_id, today
            )

            print(f"daily_submit_count: {daily_submit_count}")

            order_primary = self._generate_order_primary(user_id, daily_submit_count)

            await self.uow.quote.submit_quote(quote_id, user_id, order_primary)
            quote_model = await self.uow.quote.get_quote_by_id(quote_id)
            user_model = await self.uow.user.get_user_by_id(quote_model.user_id)

            try:

                email_service = EmailSender(
                    subject=f"Load {order_primary} Order Received",
                    receiver_email=user_model.email,
                    client_name=f"{user_model.first_name} {user_model.last_name}",
                    quote_id=quote_model.id,
                    order_primary=order_primary,
                )
                await email_service.send_email()

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"견적 제출 DB 업데이트는 성공했으나, 후속 작업(PDF/Email) 실패: {str(e)}",
                )

            return await self.get_quote_by_id(quote_id, token_data)

    async def confirm_quote(
        self,
        quote_id: str,
        role_id: int,
        request: ConfirmQuoteRequest,
        token_data: TokenData,
    ) -> GetQuoteDetailsResponse:
        # Only admin can confirm quote
        if role_id != 2:
            raise ForbiddenException(message="Admin only")

        quote_model: Optional[Quote]
        async with self.uow:
            quote_model = await self.uow.quote.get_quote_by_id(quote_id)
            if not quote_model:
                raise NotFoundException(
                    message=f"견적 ID {quote_id}를 찾을 수 없습니다. (BOL/Email 생성용)"
                )

            await self.uow.quote.confirm_quote(quote_id, request.actual_price)
            await self.uow.user.update_user_total_amount(
                user_id=quote_model.user_id, total_amount=request.actual_price
            )

            user_model = await self.uow.user.get_user_by_id(quote_model.user_id)

            quote_data_for_bol_dict = await self._prepare_bol_payload(quote_model)

            return await self.get_quote_by_id(quote_id, token_data)
