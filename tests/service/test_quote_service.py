"""
Quote 서비스 테스트
"""

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.service.quote import QuoteService
from app.service.cost import CostService
from app.repository.quote import QuoteRepository
from app.repository.quote_location import QuoteLocationRepository
from app.repository.quote_location_accessorial import QuoteLocationAccessorialRepository
from app.repository.quote_cargo import QuoteCargoRepository
from app.repository.rate_location import RateLocationRepository as RateRepository
from app.repository.user import UserRepository
from app.repository.user_level import UserLevelRepository
from app.repository.rate_area import RateAreaRepository
from app.repository.rate_area_cost import RateAreaCostRepository
from app.schema.quote import (
    CreateQuoteRequest,
    UpdateQuoteRequest,
)
from app.schema._common import (
    QuoteLocationSchema,
    QuoteCargoSchema,
    QuoteLocationAccessorialSchema,
    BaseQuoteSchema
)
from app.schema.cost.response import (
    BaseCostSchema,
    LocationCostSchema,
    ExtraCostSchema
)
from app.model._enum import LocationTypeEnum, ShipmentTypeEnum


class TestQuoteService:
    """견적 서비스 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_create_quote(self, db_session: AsyncSession):
        """견적 생성 테스트"""
        quote_repository = QuoteRepository(db_session)
        quote_location_repository = QuoteLocationRepository(db_session)
        quote_location_accessorial_repository = QuoteLocationAccessorialRepository(db_session)
        quote_cargo_repository = QuoteCargoRepository(db_session)
        rate_repository = RateRepository(db_session)
        user_repository = UserRepository(db_session)
        user_level_repository = UserLevelRepository(db_session)

        quote_service = QuoteService(
            quote_repository,
            quote_location_repository,
            quote_location_accessorial_repository,
            quote_cargo_repository
        )
        
        quote_service.db = db_session
        
        rate_area_repository = RateAreaRepository(db_session)
        rate_area_cost_repository = RateAreaCostRepository(db_session)
        cost_service = CostService(
            rate_area_repository=rate_area_repository,
            rate_area_cost_repository=rate_area_cost_repository,
            user_repository=user_repository,
            user_level_repository=user_level_repository
        )

        quote_request = CreateQuoteRequest(
            cargo_transportation_id=1,
            is_priority=True,
            from_location=QuoteLocationSchema(
                state="뉴욕",
                county="뉴욕",
                city="뉴욕시",
                zip_code="10001",
                address="123 메인 스트리트",
                location_type=LocationTypeEnum.COMMERCIAL,
                request_datetime=datetime.now(),
                accessorials=[
                    QuoteLocationAccessorialSchema(
                        cargo_accessorial_id=1,
                        name="Inside Delivery"
                    )
                ]
            ),
            to_location=QuoteLocationSchema(
                state="캘리포니아",
                county="로스앤젤레스",
                city="로스앤젤레스",
                zip_code="90001",
                address="456 새턴 애비뉴",
                location_type=LocationTypeEnum.RESIDENTIAL,
                request_datetime=datetime.now() + timedelta(days=3),
                accessorials=[
                    QuoteLocationAccessorialSchema(
                        cargo_accessorial_id=3,
                        name="Lift Gate"
                    )
                ]
            ),
            cargo=[
                QuoteCargoSchema(
                    width=100,
                    length=100,
                    height=100,
                    weight=50,
                    quantity=2,
                    package_description="테스트 패키지",
                    cargo_stackable=True,
                    cargo_temperature="상온",
                    is_hazardous=False,
                    hazardous_detail=""
                )
            ]
        )

        mock_base_cost = BaseCostSchema(
            cost=Decimal("500.00"),
            freight_weight=Decimal("100.00"),
            is_max_load=False
        )
        
        mock_location_cost = LocationCostSchema(
            cost=Decimal("50.00")
        )
        
        mock_extra_cost = ExtraCostSchema(
            cost=Decimal("100.00")
        )

        new_quote = await quote_service.create_quote(
            user_id=1,
            quote=quote_request,
            total_weight=mock_base_cost.freight_weight,
            base_price=mock_base_cost.cost,
            extra_price=mock_location_cost.cost + mock_extra_cost.cost,
            total_price_with_discount=mock_base_cost.cost + mock_location_cost.cost + mock_extra_cost.cost
        )

        assert new_quote is not None
        assert new_quote.id is not None
        assert new_quote.user_id == 1
        assert new_quote.cargo_transportation_id == quote_request.cargo_transportation_id
        assert new_quote.is_priority == quote_request.is_priority
        assert new_quote.total_weight == mock_base_cost.freight_weight
        assert new_quote.total_price == mock_base_cost.cost + mock_location_cost.cost + mock_extra_cost.cost


@pytest.fixture
def mock_repositories():
    """테스트에 필요한 레포지토리 목 객체를 생성합니다."""
    quote_repository = AsyncMock()
    quote_location_repository = AsyncMock()
    quote_location_accessorial_repository = AsyncMock()
    quote_cargo_repository = AsyncMock()
    
    return {
        'quote_repository': quote_repository,
        'quote_location_repository': quote_location_repository,
        'quote_location_accessorial_repository': quote_location_accessorial_repository,
        'quote_cargo_repository': quote_cargo_repository
    }


@pytest.fixture
def quote_service(mock_repositories):
    """테스트용 QuoteService 인스턴스를 생성합니다."""
    service = QuoteService(
        quote_repository=mock_repositories['quote_repository'],
        quote_location_repository=mock_repositories['quote_location_repository'],
        quote_location_accessorial_repository=mock_repositories['quote_location_accessorial_repository'],
        quote_cargo_repository=mock_repositories['quote_cargo_repository']
    )
    service.db = AsyncMock()
    return service


@pytest.fixture
def update_quote_request():
    """견적 업데이트 요청 객체를 생성합니다."""
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
                ),
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=3,
                    name="신규 서비스"
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
async def test_update_quote(quote_service, mock_repositories, update_quote_request):
    """견적 업데이트 기능을 테스트합니다."""
    quote_id = "TEST_QUOTE_ID"
    user_id = 1
    
    updated_quote = MagicMock()
    updated_quote.id = "TEST_QUOTE_ID"
    updated_quote.user_id = 1
    updated_quote.cargo_transportation_id = 1
    updated_quote.is_priority = True
    updated_quote.total_weight = 100
    updated_quote.base_price = 1000
    updated_quote.extra_price = 500
    updated_quote.total_price = 1500
    updated_quote.order_status = "ESTIMATE"
    updated_quote.order_primary = None
    updated_quote.order_additional_request = None
    mock_repositories['quote_repository'].update_quote.return_value = updated_quote
    
    from_location = MagicMock()
    from_location.id = 1
    to_location = MagicMock()
    to_location.id = 2
    
    mock_repositories['quote_location_repository'].get_quote_location_by_shipment_type.side_effect = [
        from_location,
        to_location
    ]
    
    from_accessorials = [
        MagicMock(cargo_accessorial_id=1),
        MagicMock(cargo_accessorial_id=2)
    ]
    
    to_accessorials = [
        MagicMock(cargo_accessorial_id=2)
    ]
    
    mock_repositories['quote_location_accessorial_repository'].get_quote_location_accessorials.side_effect = [
        from_accessorials,
        to_accessorials
    ]
    
    result = await quote_service.update_quote(
        quote_id=quote_id,
        user_id=user_id,
        quote=update_quote_request,
        total_weight=Decimal('100'),
        base_price=Decimal('1000'),
        extra_price=Decimal('500'),
        total_price_with_discount=Decimal('1500')
    )
    
    mock_repositories['quote_repository'].update_quote.assert_called_once_with(
        quote_id=quote_id,
        user_id=user_id,
        is_priority=update_quote_request.is_priority,
        cargo_transportation_id=update_quote_request.cargo_transportation_id,
        total_weight=Decimal('100'),
        base_price=Decimal('1000'),
        extra_price=Decimal('500'),
        total_price_with_discount=Decimal('1500')
    )
    
    mock_repositories['quote_location_repository'].get_quote_location_by_shipment_type.assert_any_call(
        quote_id, ShipmentTypeEnum.PICKUP
    )
    mock_repositories['quote_location_repository'].get_quote_location_by_shipment_type.assert_any_call(
        quote_id, ShipmentTypeEnum.DELIVERY
    )
    
    mock_repositories['quote_location_repository'].update_quote_location.assert_any_call(
        from_location.id, update_quote_request.from_location
    )
    mock_repositories['quote_location_repository'].update_quote_location.assert_any_call(
        to_location.id, update_quote_request.to_location
    )
    
    mock_repositories['quote_location_accessorial_repository'].delete_specific_accessorials.assert_any_call(
        from_location.id, [2]
    )
    
    mock_repositories['quote_cargo_repository'].delete_quote_cargo.assert_called_once_with(quote_id)
    mock_repositories['quote_cargo_repository'].create_quote_cargo.assert_called_once_with(
        quote_id, update_quote_request.cargo
    )
    
    assert result is not None
    assert isinstance(result, BaseQuoteSchema)


@pytest.mark.asyncio
async def test_update_accessorials_add_new(quote_service, mock_repositories):
    """부가 서비스 추가 로직을 테스트합니다."""
    location_id = 1
    
    current_accessorials = [
        MagicMock(cargo_accessorial_id=1),
        MagicMock(cargo_accessorial_id=2)
    ]
    
    new_accessorials = [
        QuoteLocationAccessorialSchema(cargo_accessorial_id=1, name="기존 서비스"),
        QuoteLocationAccessorialSchema(cargo_accessorial_id=3, name="새 서비스")
    ]
    
    mock_repositories['quote_location_accessorial_repository'].get_quote_location_accessorials.return_value = current_accessorials
    
    await quote_service._update_accessorials(location_id, new_accessorials)
    
    mock_repositories['quote_location_accessorial_repository'].delete_specific_accessorials.assert_called_once_with(
        location_id, [2]
    )
    
    mock_repositories['quote_location_accessorial_repository'].create_quote_location_accessorial.assert_called_once()
    called_location_id, called_accessorials = mock_repositories['quote_location_accessorial_repository'].create_quote_location_accessorial.call_args[0]
    assert called_location_id == location_id
    assert len(called_accessorials) == 1
    assert called_accessorials[0].cargo_accessorial_id == 3


@pytest.mark.asyncio
async def test_update_accessorials_remove_all(quote_service, mock_repositories):
    """모든 부가 서비스 삭제 로직을 테스트합니다."""
    location_id = 1
    
    current_accessorials = [
        MagicMock(cargo_accessorial_id=1),
        MagicMock(cargo_accessorial_id=2)
    ]
    
    new_accessorials = []
    
    mock_repositories['quote_location_accessorial_repository'].get_quote_location_accessorials.return_value = current_accessorials
    
    await quote_service._update_accessorials(location_id, new_accessorials)
    
    mock_repositories['quote_location_accessorial_repository'].delete_specific_accessorials.assert_called_once_with(
        location_id, [1, 2]
    )
    
    mock_repositories['quote_location_accessorial_repository'].create_quote_location_accessorial.assert_not_called()