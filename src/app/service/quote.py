from decimal import Decimal
from pprint import pprint
from typing import List, Optional

from fastapi import HTTPException

from app.service.bol import create_structured_bill_of_lading
import os
from ..db.unit_of_work import UnitOfWork
from ..model.quote import Quote # Optional[Quote] 타입을 위해 명시적 임포트
from ..core.exceptions import NotFoundException
from ..model._enum import ShipmentTypeEnum
from ..schema._common import BaseQuoteSchema, QuoteLocationAccessorialSchema # BaseQuoteSchema는 응답 타입으로 직접 사용될 수 있음
from ..schema.quote.request import CreateQuoteRequest, UpdateQuoteRequest # 요청 스키마 경로 수정
from ..schema.quote.response import ( # 응답 스키마 경로 수정 및 명시적 임포트
    GetQuotesResponse,
    GetQuoteDetailsResponse,
    QuoteLocationWithIDSchema,
    QuoteCargoWithIDSchema,
    GetQuotesLocationSchema
)
from app.service.email import EmailSender # 주석 해제

class QuoteService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow
        
    async def get_quotes(self, user_id: int) -> List[GetQuotesResponse]:
        async with self.uow:
            quote_models = await self.uow.quotes.get_quotes(user_id)
            response_list = []
            for quote_model in quote_models:
                from_location_data = None
                to_location_data = None
                for loc_model in quote_model.quote_location: # quote_model.quote_location은 List[QuoteLocation]
                    # GetQuotesLocationSchema에 맞게 데이터 변환
                    loc_schema_data = GetQuotesLocationSchema.model_validate(loc_model) # from_attributes=True 가정
                    if loc_model.shipment_type == ShipmentTypeEnum.PICKUP:
                        from_location_data = loc_schema_data
                    elif loc_model.shipment_type == ShipmentTypeEnum.DELIVERY:
                        to_location_data = loc_schema_data
                
                if not from_location_data or not to_location_data:
                    # 필수 위치 정보가 없는 경우의 처리 (예: 로깅, 예외 발생 또는 빈 값으로 설정)
                    # 여기서는 일단 필수라고 가정하고, 둘 다 있어야 GetQuotesResponse를 만든다고 가정
                    # 혹은 스키마에서 Optional로 정의되어 있다면 None으로 둘 수 있음
                    # 현재 스키마 GetQuotesResponse는 from_location, to_location이 Optional이 아님
                    continue # 또는 적절한 예외 처리

                # BaseQuoteSchema 부분은 quote_model에서 가져오고, from/to_location은 위에서 준비한 데이터 사용
                response_list.append(
                    GetQuotesResponse(
                        # **quote_model.model_dump(exclude={'quote_location', 'quote_cargo'}), # 기존 필드들
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
                        to_location=to_location_data
                    )
                )
            return response_list

    async def get_quote_by_id(self, quote_id: str, user_id: int) -> GetQuoteDetailsResponse:
        async with self.uow:
            quote_model = await self.uow.quotes.get_quote_by_id(quote_id, user_id)
            pprint(quote_model.__dict__)
            quote_location_models = quote_model.quote_location
            pprint(quote_location_models[0].__dict__)
            pprint(quote_location_models[1].__dict__)
            quote_cargo_models = quote_model.quote_cargo
            pprint(quote_cargo_models[0].__dict__)
            if quote_model is None:
                raise NotFoundException(message="견적을 찾을 수 없습니다.")

            from_location_detail = None
            to_location_detail = None
            for loc_model in quote_model.quote_location:
                # accessorials 정보를 가져와서 스키마 생성 시 포함
                accessorial_models = await self.uow.quote_location_accessorials.get_quote_location_accessorials(loc_model.id)
                accessorial_schemas = [
                    QuoteLocationAccessorialSchema(
                        cargo_accessorial_id=acc.cargo_accessorial_id,
                        name=acc.cargo_accessorial.name
                    ) for acc in accessorial_models
                ]

                loc_detail_schema = QuoteLocationWithIDSchema(
                    id=loc_model.id,
                    state=loc_model.state,
                    county=loc_model.county,
                    city=loc_model.city,
                    zip_code=loc_model.zip_code,
                    address=loc_model.address,
                    location_type=loc_model.location_type,
                    request_datetime=loc_model.request_datetime,
                    accessorials=accessorial_schemas
                )
                if loc_model.shipment_type == ShipmentTypeEnum.PICKUP:
                    from_location_detail = loc_detail_schema
                elif loc_model.shipment_type == ShipmentTypeEnum.DELIVERY:
                    to_location_detail = loc_detail_schema
            
            if not from_location_detail or not to_location_detail:
                # 필수 위치 정보가 없는 경우의 처리
                raise NotFoundException(message=f"견적 {quote_id}의 출발지 또는 도착지 정보를 찾을 수 없습니다.")

            cargo_details = []
            if hasattr(quote_model, 'quote_cargo'):
                for qc_model in quote_model.quote_cargo:
                    # QuoteCargoWithIDSchema에 맞게 데이터 변환
                    cargo_details.append(QuoteCargoWithIDSchema.model_validate(qc_model)) # from_attributes=True 가정
            
            # GetQuoteDetailsResponse 구성
            # BaseQuoteSchema 부분은 quote_model에서 가져오고, 나머지는 위에서 준비한 데이터 사용
            return GetQuoteDetailsResponse(
                # **quote_model.model_dump(exclude={'quote_location', 'quote_cargo'}), # 기존 필드들
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
                cargo=cargo_details
            )

    async def create_quote(
        self,
        user_id: int,
        quote_data: CreateQuoteRequest,
        total_weight: Decimal,
        base_price: Decimal,
        extra_price: Decimal,
        total_price_with_discount: Decimal,
    ) -> BaseQuoteSchema: # 반환 타입을 다시 BaseQuoteSchema로 변경
        async with self.uow:
            new_quote_model = await self.uow.quotes.create_quote(
                user_id=user_id,
                total_weight=total_weight,
                base_price=base_price,
                extra_price=extra_price,
                total_price_with_discount=total_price_with_discount,
                quote_payload=quote_data,
            )
            
            await self.uow.quote_locations.create_quote_location(
                new_quote_model.id, quote_data.from_location, ShipmentTypeEnum.PICKUP
            )
            await self.uow.quote_location_accessorials.create_quote_location_accessorial(
                (await self.uow.quote_locations.get_quote_location_by_shipment_type(new_quote_model.id, ShipmentTypeEnum.PICKUP)).id, 
                quote_data.from_location.accessorials
            )
            await self.uow.quote_locations.create_quote_location(
                new_quote_model.id, quote_data.to_location, ShipmentTypeEnum.DELIVERY
            )
            await self.uow.quote_location_accessorials.create_quote_location_accessorial(
                (await self.uow.quote_locations.get_quote_location_by_shipment_type(new_quote_model.id, ShipmentTypeEnum.DELIVERY)).id, 
                quote_data.to_location.accessorials
            )
            await self.uow.quote_cargos.create_quote_cargo(new_quote_model.id, quote_data.cargo)
            
            # 생성된 Quote 모델을 BaseQuoteSchema로 변환하여 반환 (원래대로)
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
    ) -> GetQuoteDetailsResponse: # 반환 타입을 GetQuoteDetailsResponse로 변경
        async with self.uow:
            updated_quote_model = await self.uow.quotes.update_quote(
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
                raise NotFoundException(message=f"견적 ID {quote_id}를 업데이트하거나 찾을 수 없습니다.")

            # from_location, to_location, cargo 정보 업데이트
            from_location_model = (
                await self.uow.quote_locations.get_quote_location_by_shipment_type(
                    quote_id, ShipmentTypeEnum.PICKUP
                )
            )
            if from_location_model is None: # 방어 코드: 없을 경우 새로 생성 또는 오류
                # 여기서는 UpdateQuoteRequest에 정보가 있으므로 새로 만들 수도 있으나, 보통은 update 대상이 있어야 함.
                # 일단 NotFound로 처리. 만약 upsert 개념이라면 로직 변경 필요.
                raise NotFoundException(message=f"견적 {quote_id}의 출발지 정보를 찾을 수 없습니다.")
            await self.uow.quote_locations.update_quote_location(
                from_location_model.id, quote_data.from_location
            )
            await self._update_accessorials(
                from_location_model.id, quote_data.from_location.accessorials
            )

            to_location_model = (
                await self.uow.quote_locations.get_quote_location_by_shipment_type(
                    quote_id, ShipmentTypeEnum.DELIVERY
                )
            )
            if to_location_model is None: 
                raise NotFoundException(message=f"견적 {quote_id}의 도착지 정보를 찾을 수 없습니다.")
            await self.uow.quote_locations.update_quote_location(
                to_location_model.id, quote_data.to_location
            )
            await self._update_accessorials(to_location_model.id, quote_data.to_location.accessorials)

            await self.uow.quote_cargos.delete_quote_cargo(quote_id) # 기존 cargo 삭제
            created_cargos_models = await self.uow.quote_cargos.create_quote_cargo(quote_id, quote_data.cargo) # 새 cargo 생성
            
            # 업데이트된 모든 정보를 포함하여 GetQuoteDetailsResponse 구성
            # from_location_model, to_location_model에서 accessorials 정보를 가져와 스키마에 포함
            
            # from_location의 accessorials 가져오기
            from_accessorial_models = await self.uow.quote_location_accessorials.get_quote_location_accessorials(from_location_model.id)
            from_accessorial_schemas = [
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=acc.cargo_accessorial_id,
                    name=acc.cargo_accessorial.name # CargoAccessorial 모델에서 name 가져오기
                ) for acc in from_accessorial_models
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
                accessorials=from_accessorial_schemas
            )

            # to_location의 accessorials 가져오기
            to_accessorial_models = await self.uow.quote_location_accessorials.get_quote_location_accessorials(to_location_model.id)
            to_accessorial_schemas = [
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=acc.cargo_accessorial_id,
                    name=acc.cargo_accessorial.name # CargoAccessorial 모델에서 name 가져오기
                ) for acc in to_accessorial_models
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
                accessorials=to_accessorial_schemas
            )
            
            cargo_details_schemas = []
            for qc_model in created_cargos_models: # create_quote_cargo의 반환값 사용
                cargo_details_schemas.append(QuoteCargoWithIDSchema.model_validate(qc_model))

            return GetQuoteDetailsResponse(
                # **updated_quote_model.model_dump(exclude={'quote_location', 'quote_cargo'}),
                id=updated_quote_model.id,
                user_id=updated_quote_model.user_id,
                cargo_transportation_id=updated_quote_model.cargo_transportation_id,
                is_priority=updated_quote_model.is_priority,
                total_weight=updated_quote_model.total_weight,
                base_price=updated_quote_model.base_price,
                extra_price=updated_quote_model.extra_price,
                total_price=updated_quote_model.total_price, # Quote 모델의 실제 최종 가격 필드로 수정 (total_price_with_discount -> total_price)
                order_status=updated_quote_model.order_status,
                order_primary=updated_quote_model.order_primary,
                order_additional_request=updated_quote_model.order_additional_request,
                from_location=from_location_schema,
                to_location=to_location_schema,
                cargo=cargo_details_schemas
            )

    async def _update_accessorials(self, location_id: int, new_accessorials: List[QuoteLocationAccessorialSchema]):
        current_accessorials = await self.uow.quote_location_accessorials.get_quote_location_accessorials(
            location_id
        )
        # new_accessorials는 스키마 객체 리스트이므로 cargo_accessorial_id를 직접 접근
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
            if acc_schema.cargo_accessorial_id in (new_cargo_accessorial_ids - current_cargo_accessorial_ids)
        ]

        if to_delete_ids: # ID 리스트로 변경
            await self.uow.quote_location_accessorials.delete_specific_accessorials(
                location_id, list(to_delete_ids)
            )
        if to_add_schemas: # 스키마 리스트 전달
            await self.uow.quote_location_accessorials.create_quote_location_accessorial(
                location_id, to_add_schemas
            )

    async def submit_quote(self, quote_id: str, user_id: int) -> GetQuoteDetailsResponse:
        raw_quote_model_for_bol: Optional[Quote]
        async with self.uow:
            raw_quote_model_for_bol = await self.uow.quotes.get_quote_by_id(quote_id, user_id)
            if not raw_quote_model_for_bol:
                raise NotFoundException(message=f"견적 ID {quote_id}를 찾을 수 없습니다. (BOL 생성용)")
            
            await self.uow.quotes.submit_quote(quote_id, user_id)

        pdf_path = "structured_bill_of_lading.pdf"
        try:
            # BOL 생성을 위한 payload 구성 (GetQuoteDetailsResponse 스키마와 유사하게)
            # from_location, to_location, cargo 등을 raw_quote_model_for_bol에서 추출하여 구성
            
            from_loc_bol_schema = None
            to_loc_bol_schema = None
            for loc_model in raw_quote_model_for_bol.quote_location:
                # QuoteLocationWithIDSchema를 사용하여 BOL용 데이터 구성
                loc_schema = QuoteLocationWithIDSchema.model_validate(loc_model)
                if loc_model.shipment_type == ShipmentTypeEnum.PICKUP:
                    from_loc_bol_schema = loc_schema
                elif loc_model.shipment_type == ShipmentTypeEnum.DELIVERY:
                    to_loc_bol_schema = loc_schema
            
            if not from_loc_bol_schema or not to_loc_bol_schema:
                 raise NotFoundException(message=f"견적 {quote_id}의 BOL 생성을 위한 위치 정보를 찾을 수 없습니다.")

            cargo_bol_schemas = []
            if hasattr(raw_quote_model_for_bol, 'quote_cargo'):
                for qc_model in raw_quote_model_for_bol.quote_cargo:
                    cargo_bol_schemas.append(QuoteCargoWithIDSchema.model_validate(qc_model))

            # create_structured_bill_of_lading이 dict를 받는다고 가정하고 .model_dump() 사용
            # BaseQuoteSchema 부분도 포함
            quote_data_for_bol_dict = BaseQuoteSchema.model_validate(raw_quote_model_for_bol).model_dump()

            # from_location, to_location, cargo를 dict에 추가
            quote_data_for_bol_dict["from_location"] = from_loc_bol_schema.model_dump() if from_loc_bol_schema else None
            quote_data_for_bol_dict["to_location"] = to_loc_bol_schema.model_dump() if to_loc_bol_schema else None
            quote_data_for_bol_dict["cargo"] = [c.model_dump() for c in cargo_bol_schemas]
            
            # Enum 값 처리 등 추가적인 직렬화 고려
            # 예: quote_data_for_bol_dict["order_status"] = raw_quote_model_for_bol.order_status.value

            await create_structured_bill_of_lading(quote_data_for_bol_dict, pdf_path)
            
            # EmailSender 부분은 EmailSender 구현 확인 후 활성화
            email_service = EmailSender(
                subject="BeyondX 견적서 제출 완료",
                receiver_email="wang323@naver.com", # 실제로는 사용자 이메일 등 사용
                client_id=raw_quote_model_for_bol.id, # 견적 ID 또는 사용자 ID 등
                quote=raw_quote_model_for_bol.total_price, # Decimal 처리 주의
                pdf_buffer=open(pdf_path, "rb").read(),
                pdf_filename=os.path.basename(pdf_path)
            )
            await email_service.send_email()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"견적 제출 후 작업(PDF/Email) 실패: {str(e)}")
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        
        return await self.get_quote_by_id(quote_id, user_id)
