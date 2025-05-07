"""
Quote API 테스트
"""

import pytest
import uuid
from decimal import Decimal
from fastapi import status, HTTPException
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.schema.cost.response import BaseCostSchema
from app.model._enum import LocationTypeEnum, ShipmentTypeEnum
from app.schema.quote import UpdateQuoteRequest
from app.schema._common import QuoteLocationSchema
from app.schema._common import QuoteCargoSchema
from app.schema._common import QuoteLocationAccessorialSchema


@pytest.fixture
def mock_quote_request():
    return UpdateQuoteRequest(
        cargo_transportation_id=1,
        is_priority=True,
        from_location=QuoteLocationSchema(
            state="경기도",
            county="성남시",
            city="분당구",
            zip_code="13561",
            address="판교로 228번길",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=datetime.now(),
            accessorials=[
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=1,
                    name="리프트 게이트"
                )
            ]
        ),
        to_location=QuoteLocationSchema(
            state="서울",
            county="강남구",
            city="역삼동",
            zip_code="06142",
            address="테헤란로 521",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=datetime.now(),
            accessorials=[
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=2,
                    name="하역 서비스"
                )
            ]
        ),
        cargo=[
            QuoteCargoSchema(
                width=100,
                length=100,
                height=100,
                weight=100,
                quantity=1,
                package_description="테스트 화물",
                cargo_stackable=True,
                cargo_temperature="상온",
                is_hazardous=False,
                hazardous_detail=""
            )
        ]
    )


@pytest.mark.asyncio
class TestQuoteAPI:
    """Quote API 테스트 클래스"""

    async def test_create_quote_max_load_exception(self, client):
        """최대 로드 초과 시 HTTP 예외 발생 테스트"""
        # Given: cost_service.calculate_base_cost가 is_max_load=True를 반환하도록 패치
        with patch("app.service.cost.CostService.calculate_base_cost") as mock_calculate_base_cost:
            # 모의 응답 설정
            mock_calculate_base_cost.return_value = BaseCostSchema(
                cost=Decimal("1000"), freight_weight=Decimal("100"), is_max_load=True
            )
            
            # 요청 데이터 설정
            request_data = {
                "cargo_transportation_id": 1,
                "is_priority": False,
                "cargo": [
                    {
                        "width": 10,
                        "length": 10,
                        "height": 10,
                        "weight": 100,
                        "quantity": 1,
                        "package_description": "테스트 화물",
                        "cargo_stackable": False,
                        "cargo_temperature": "상온",
                        "is_hazardous": False,
                        "hazardous_detail": ""
                    }
                ],
                "from_location": {
                    "zip_code": "12345",
                    "location_type": "RESIDENTIAL",
                    "state": "뉴욕",
                    "county": "뉴욕",
                    "city": "뉴욕시",
                    "address": "123 메인 스트리트",
                    "request_datetime": "2023-06-07T14:00:00",
                    "accessorials": [],
                },
                "to_location": {
                    "zip_code": "67890",
                    "location_type": "COMMERCIAL",
                    "state": "뉴저지",
                    "county": "뉴저지",
                    "city": "뉴저지시",
                    "address": "456 서브 스트리트",
                    "request_datetime": "2023-06-07T14:00:00",
                    "accessorials": [],
                }
            }

            # When: API 요청 실행
            response = await client.post(
                "/api/quote", 
                json=request_data,
                headers={"Authorization": "Bearer test_token"}
            )
            
            # 응답 상태 코드와 응답 내용 출력
            print(f"응답 상태 코드: {response.status_code}")
            print(f"응답 내용: {response.json()}")

            # Then: 결과 검증 (이제 422 대신 400으로 예상됨)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "최대 금액을 초과했습니다" in response.json()["message"]

            # 호출 확인
            mock_calculate_base_cost.assert_called_once()

    async def test_update_quote_success(self, mock_quote_request):
        """견적 업데이트 API가 성공적으로 동작하는지 테스트합니다."""
        from app.api.quote import update_quote
        
        # Mock 객체 준비
        cost_service = AsyncMock()
        quote_service = AsyncMock()
        token_data = MagicMock()
        token_data.user_id = 1
        
        # 기존 견적 존재 설정
        mock_quote = MagicMock()
        quote_service.get_quote_by_id.return_value = mock_quote
        
        # 비용 계산 결과 설정
        base_cost = MagicMock()
        base_cost.cost = Decimal('1000')
        base_cost.freight_weight = Decimal('100')
        base_cost.is_max_load = False
        
        location_type_cost = MagicMock()
        location_type_cost.cost = Decimal('200')
        
        extra_cost = MagicMock()
        extra_cost.cost = Decimal('300')
        
        total_price_with_discount = MagicMock()
        total_price_with_discount.cost = Decimal('1500')
        
        cost_service.calculate_base_cost.return_value = base_cost
        cost_service.calculate_location_type_cost.return_value = location_type_cost
        cost_service.calculate_extra_cost.return_value = extra_cost
        cost_service.calculate_discount.return_value = total_price_with_discount
        
        # 업데이트된 견적 설정
        updated_quote = MagicMock()
        quote_service.update_quote.return_value = updated_quote
        
        # 함수 실행
        result = await update_quote(
            cost_service=cost_service,
            quote_service=quote_service,
            token_data=token_data,
            request=mock_quote_request,
            quote_id="TEST_QUOTE_ID"
        )
        
        # 검증
        assert result == updated_quote
        quote_service.get_quote_by_id.assert_called_once_with("TEST_QUOTE_ID", 1)
        cost_service.calculate_base_cost.assert_called_once()
        cost_service.calculate_location_type_cost.assert_called_once()
        cost_service.calculate_extra_cost.assert_called_once()
        cost_service.calculate_discount.assert_called_once()
        quote_service.update_quote.assert_called_once()

    async def test_update_quote_not_found(self, mock_quote_request):
        """존재하지 않는 견적 ID로 요청 시 404 오류가 발생하는지 테스트합니다."""
        from app.api.quote import update_quote
        from app.core.exceptions import NotFoundException

        # Mock 객체 준비
        cost_service = AsyncMock()
        quote_service = AsyncMock()
        token_data = MagicMock()
        token_data.user_id = 1

        # 견적이 존재하지 않음
        quote_service.get_quote_by_id.return_value = None

        # 새로 patching
        with patch('app.api.quote.NotFoundException', new=lambda message, **kwargs: HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )):
            # 함수 실행 및 예외 검증
            with pytest.raises(HTTPException) as exc_info:
                await update_quote(
                    cost_service=cost_service,
                    quote_service=quote_service,
                    token_data=token_data,
                    request=mock_quote_request,
                    quote_id="NONEXISTENT_QUOTE_ID"
                )
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "해당 견적을 찾을 수 없습니다" in exc_info.value.detail

    async def test_update_quote_max_load_exceeded(self, mock_quote_request):
        """최대 금액 초과 시 400 오류가 발생하는지 테스트합니다."""
        from app.api.quote import update_quote
        
        # Mock 객체 준비
        cost_service = AsyncMock()
        quote_service = AsyncMock()
        token_data = MagicMock()
        token_data.user_id = 1
        
        # 기존 견적 존재 설정
        mock_quote = MagicMock()
        quote_service.get_quote_by_id.return_value = mock_quote
        
        # 최대 금액 초과 설정
        base_cost = MagicMock()
        base_cost.is_max_load = True
        cost_service.calculate_base_cost.return_value = base_cost
        
        # 함수 실행 및 예외 검증
        with pytest.raises(HTTPException) as exc_info:
            await update_quote(
                cost_service=cost_service,
                quote_service=quote_service,
                token_data=token_data,
                request=mock_quote_request,
                quote_id="TEST_QUOTE_ID"
            )
        
        assert exc_info.value.status_code == 400
        assert "최대 금액을 초과했습니다" in exc_info.value.detail
