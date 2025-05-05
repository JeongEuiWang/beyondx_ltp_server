"""
Quote 서비스 테스트
"""

import pytest
import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.quote import QuoteService
from app.service.cost import CostService
from app.repository.quote import QuoteRepository
from app.repository.quote_location import QuoteLocationRepository
from app.repository.quote_cargo import QuoteCargoRepository
from app.repository.rate import RateRepository
from app.schema.quote import (
    CreateQuoteRequest,
    QuoteLocationRequest,
    QuoteCargoRequest,
    QuoteLocationAccessorialRequest,
)
from app.schema.cost import BaseCost, LocationCost, ExtraCost
from app.model._enum import LocationTypeEnum, ShipmentTypeEnum


class TestQuoteService:
    """견적 서비스 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_create_quote(self, db_session: AsyncSession):
        """견적 생성 테스트"""
        # 리포지토리 인스턴스 생성
        quote_repository = QuoteRepository(db_session)
        quote_location_repository = QuoteLocationRepository(db_session)
        quote_cargo_repository = QuoteCargoRepository(db_session)
        rate_repository = RateRepository(db_session)

        # 서비스 인스턴스 생성
        quote_service = QuoteService(
            quote_repository,
            quote_location_repository,
            quote_cargo_repository
        )
        
        # @transactional 데코레이터를 위한 db 속성 설정
        quote_service.db = db_session
        
        cost_service = CostService(rate_repository)

        # 테스트용 견적 요청 데이터 생성
        # 실제 DB에서 확인한 ID 값 사용
        quote_request = CreateQuoteRequest(
            cargo_transportation_id=1,  # LTL (확인됨)
            is_priority=True,
            from_location=QuoteLocationRequest(
                state="뉴욕",
                county="뉴욕",
                city="뉴욕시",
                zip_code="10001",  # 테스트용 ZIP 코드
                address="123 메인 스트리트",
                location_type=LocationTypeEnum.COMMERCIAL,
                request_datetime=datetime.datetime.now(),
                accessorials=[
                    QuoteLocationAccessorialRequest(
                        cargo_accessorial_id=1,  # Inside Delivery (확인됨)
                        name="Inside Delivery"
                    )
                ]
            ),
            to_location=QuoteLocationRequest(
                state="캘리포니아",
                county="로스앤젤레스",
                city="로스앤젤레스",
                zip_code="90001",  # 테스트용 ZIP 코드
                address="456 새턴 애비뉴",
                location_type=LocationTypeEnum.RESIDENTIAL,
                request_datetime=datetime.datetime.now() + datetime.timedelta(days=3),
                accessorials=[
                    QuoteLocationAccessorialRequest(
                        cargo_accessorial_id=3,  # Lift Gate (확인됨)
                        name="Lift Gate"
                    )
                ]
            ),
            cargo=[
                QuoteCargoRequest(
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

        # 테스트 시작: 비용 계산을 위한 모의 객체(mock) 사용
        # 실제 데이터베이스 접근 없이 테스트할 수 있도록 모의 비용 객체 생성
        mock_base_cost = BaseCost(
            cost=Decimal("500.00"),
            freight_weight=Decimal("100.00"),
            is_max_load=False
        )
        
        mock_location_cost = LocationCost(
            cost=Decimal("50.00")
        )
        
        mock_extra_cost = ExtraCost(
            cost=Decimal("100.00")
        )

        # 테스트 실행: 견적 생성
        new_quote = await quote_service.create_quote(
            user_id=1,  # 테스트용 사용자 ID
            quote=quote_request,
            base_cost=mock_base_cost,
            location_type_cost=mock_location_cost,
            extra_cost=mock_extra_cost
        )

        # 검증
        assert new_quote is not None
        assert new_quote.id is not None
        assert new_quote.user_id == 1
        assert new_quote.cargo_transportation_id == quote_request.cargo_transportation_id
        assert new_quote.is_priority == quote_request.is_priority
        assert new_quote.total_weight == mock_base_cost.freight_weight
        assert new_quote.total_price == mock_base_cost.cost + mock_location_cost.cost + mock_extra_cost.cost

        # 데이터베이스에서 생성된 견적 정보 확인
        # 추가 검증을 위해 필요하다면 다음 쿼리를 수행할 수 있습니다
        # statement = select(Quote).where(Quote.id == new_quote.id)
        # result = await db_session.execute(statement)
        # fetched_quote = result.scalar_one_or_none()
        # assert fetched_quote is not None 