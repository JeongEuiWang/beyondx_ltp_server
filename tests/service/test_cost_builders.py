"""
Cost Builder 테스트
"""

import pytest
import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from app.service.cost_builder.base_cost_builder import BaseCostBuilder
from app.service.cost_builder.location_type_cost_builder import LocationCostBuilder
from app.service.cost_builder.extra_cost_builder import ExtraCostBuilder
from app.schema.cost import BaseCost, RateCost
from app.schema.quote import QuoteLocationRequest, QuoteLocationAccessorialRequest
from app.model._enum import LocationTypeEnum


class TestBaseCostBuilder:
    """BaseCostBuilder 테스트 클래스"""

    def test_set_freight_weight(self):
        """화물 무게 계산 테스트"""
        # Builder 생성
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        
        # 케이스 1: 패키지 무게가 더 큰 경우
        builder.set_freight_weight(weight=50, quantity=2, width=10, height=10, length=10)
        # 패키지 무게: 50 * 2 = 100
        # 부피 무게: 10 * 10 * 10 / 166 = 6.02...
        assert builder._freight_weight == Decimal("100")
        
        # 케이스 2: 부피 무게가 더 큰 경우
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder.set_freight_weight(weight=1, quantity=1, width=100, height=100, length=100)
        # 패키지 무게: 1 * 1 = 1
        # 부피 무게: 100 * 100 * 100 / 166 = 6024.096...
        assert builder._freight_weight == Decimal("6024.097")
    
    def test_set_price_per_weight(self):
        """가격/무게 비율 계산 테스트"""
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_weight = Decimal("100")
        # _max_load_weight 값을 설정하여 예외가 발생하지 않도록 함
        builder._max_load_weight = Decimal("200")
        
        # 테스트 요율 설정
        rate_costs = [
            RateCost(min_weight=Decimal("0"), max_weight=Decimal("50"), price_per_weight=Decimal("5")),
            RateCost(min_weight=Decimal("51"), max_weight=Decimal("150"), price_per_weight=Decimal("4")),
            RateCost(min_weight=Decimal("151"), max_weight=Decimal("500"), price_per_weight=Decimal("3"))
        ]
        
        # 무게 100은 두 번째 요율에 해당
        builder.set_price_per_weight(rate_costs)
        assert builder._price_per_weight == Decimal("4")
        
        # 무게가 요율 범위에 없는 경우
        builder._freight_weight = Decimal("1000")
        # 최대 무게도 그에 맞게 증가시킴
        builder._max_load_weight = Decimal("1500")
        builder.set_price_per_weight(rate_costs)
        # 조건에 맞는 rate_cost가 없으면 price_per_weight는 변경되지 않음
        assert builder._price_per_weight == Decimal("4")
    
    def test_set_price_per_weight_exceeds_max_weight(self):
        # Given
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        
        # 최대 무게를 초과하는 상황 설정
        builder._freight_weight = Decimal("1000")
        builder._max_load_weight = Decimal("500")
        
        rate_costs = [
            RateCost(min_weight=Decimal("0"), max_weight=Decimal("1000"), price_per_weight=Decimal("10"))
        ]
        
        # When/Then
        with pytest.raises(Exception) as excinfo:
            builder.set_price_per_weight(rate_costs)
        
        assert "최대 운임 무게를 초과했습니다" in str(excinfo.value)
    
    def test_calculate_base_cost(self):
        """기본 비용 계산 테스트"""
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_weight = Decimal("100")
        builder._price_per_weight = Decimal("5")
        builder._min_load = Decimal("400")
        builder._max_load = Decimal("800")
        
        # 케이스 1: 기본 비용이 최소 로드보다 작은 경우
        # 100 * 5 = 500, 이는 min_load(400)보다 크고 max_load(800)보다 작음
        builder.calculate_base_cost()
        assert builder._freight_cost == Decimal("500")
        assert builder._is_max_load == False
        
        # 케이스 2: 기본 비용이 최소 로드보다 작은 경우
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_weight = Decimal("50")
        builder._price_per_weight = Decimal("5")
        builder._min_load = Decimal("400")
        builder._max_load = Decimal("800")
        
        # 50 * 5 = 250, 이는 min_load(400)보다 작음
        builder.calculate_base_cost()
        assert builder._freight_cost == Decimal("400") # min_load로 설정됨
        assert builder._is_max_load == False
        
        # 케이스 3: 기본 비용이 최대 로드보다 큰 경우
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_weight = Decimal("200")
        builder._price_per_weight = Decimal("5")
        builder._min_load = Decimal("400")
        builder._max_load = Decimal("800")
        
        # 200 * 5 = 1000, 이는 max_load(800)보다 큼
        builder.calculate_base_cost()
        assert builder._freight_cost == Decimal("800") # max_load로 설정됨
        assert builder._is_max_load == True
    
    def test_calculate_with_fsc(self):
        """연료 할증료 계산 테스트"""
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_cost = Decimal("500")
        
        # 500 * (1 + 0.35) = 675
        builder.calculate_with_fsc()
        assert builder._final_cost == Decimal("675")
    
    def test_full_calculation(self):
        """전체 계산 프로세스 테스트"""
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        
        # 화물 무게 설정
        builder.set_freight_weight(weight=50, quantity=2, width=10, height=10, length=10)
        
        # 지역 요율 설정
        builder.set_location_rate(
            min_load=Decimal("400"), 
            max_load=Decimal("800"),
            max_load_weight=Decimal("200")
        )
        
        # 무게당 가격 설정
        rate_costs = [
            RateCost(min_weight=Decimal("0"), max_weight=Decimal("50"), price_per_weight=Decimal("5")),
            RateCost(min_weight=Decimal("51"), max_weight=Decimal("150"), price_per_weight=Decimal("4")),
            RateCost(min_weight=Decimal("151"), max_weight=Decimal("500"), price_per_weight=Decimal("3"))
        ]
        builder.set_price_per_weight(rate_costs)
        
        # 기본 비용 계산
        builder.calculate_base_cost()
        
        # FSC 적용
        builder.calculate_with_fsc()
        
        # 결과 계산
        result = builder.calculate()
        
        # 검증
        assert result.freight_weight == Decimal("100")
        assert result.cost == Decimal("540") # 100 * 4 = 400, 400 * 1.35 = 540
        assert result.is_max_load == False


class TestLocationCostBuilder:
    """LocationCostBuilder 테스트 클래스"""

    def test_commercial_location(self):
        """상업 지역 비용 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.COMMERCIAL, "PICK_UP")
        
        # 상업 지역은 추가 비용 없음
        assert builder._final_cost == Decimal("0")
        
        result = builder.calculate()
        assert result.cost == Decimal("0")
    
    def test_residential_location(self):
        """주거 지역 비용 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.RESIDENTIAL, "PICK_UP")
        
        # 주거 지역은 상수 비용 적용
        assert builder._final_cost == Decimal("25")
        
        result = builder.calculate()
        assert result.cost == Decimal("25")
    
    def test_airport_location_pickup(self):
        """공항 픽업 비용 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.AIRPORT, "PICK_UP")
        
        # 공항 픽업 계산: 100 * 0.035 = 3.5, 최소값 30 적용
        assert builder._final_cost == Decimal("30")
        
        # 무게가 큰 경우
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("10000"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.AIRPORT, "PICK_UP")
        
        # 공항 픽업 계산: 10000 * 0.035 = 350, 최대값 200 적용
        assert builder._final_cost == Decimal("200")
    
    def test_airport_location_delivery(self):
        """공항 배송 비용 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("1000"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.AIRPORT, "DELIVERY")
        
        # 공항 배송 계산: 1000 * 0.03 = 30
        assert builder._final_cost == Decimal("30")
        
        # 최소/최대 값 테스트
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("500"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.AIRPORT, "DELIVERY")
        
        # 500 * 0.03 = 15, 최소값 25 적용
        assert builder._final_cost == Decimal("25")
    
    def test_multiple_location_types(self):
        """여러 위치 유형 조합 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.RESIDENTIAL, "PICK_UP")
        builder.check_location_type(LocationTypeEnum.AIRPORT, "DELIVERY")
        
        # 주거 지역 픽업 + 공항 배송
        # 25 (주거) + 25 (공항 배송 최소값) = 50
        assert builder._final_cost == Decimal("50")
        
        result = builder.calculate()
        assert result.cost == Decimal("50")


class TestExtraCostBuilder:
    """ExtraCostBuilder 테스트 클래스"""

    def test_accessorial_costs(self):
        """부가 서비스 비용 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        # Inside Delivery 테스트
        location = QuoteLocationRequest(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=datetime.datetime.now(),
            accessorials=[
                QuoteLocationAccessorialRequest(
                    cargo_accessorial_id=1,
                    name="Inside Delivery"
                )
            ]
        )
        
        builder.calculate_accesserial(location)
        # Inside Delivery: max(25, 100 * 0.02) = max(25, 2) = 25
        assert builder._final_cost == Decimal("25")
        
        # Two Person 추가
        location.accessorials.append(
            QuoteLocationAccessorialRequest(
                cargo_accessorial_id=2,
                name="Two Person"
            )
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_accesserial(location)
        # Inside Delivery + Two Person = 25 + 80 = 105
        assert builder._final_cost == Decimal("105")
        
        # Lift Gate 추가
        location.accessorials.append(
            QuoteLocationAccessorialRequest(
                cargo_accessorial_id=3,
                name="Lift Gate"
            )
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_accesserial(location)
        # Inside Delivery + Two Person + Lift Gate = 25 + 80 + 25 = 130
        assert builder._final_cost == Decimal("130")
    
    def test_inside_delivery_weight_based(self):
        """Inside Delivery가 무게에 따라 계산되는 경우 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("2000"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        # 무게가 큰 경우 Inside Delivery 비용 테스트
        location = QuoteLocationRequest(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=datetime.datetime.now(),
            accessorials=[
                QuoteLocationAccessorialRequest(
                    cargo_accessorial_id=1,
                    name="Inside Delivery"
                )
            ]
        )
        
        builder.calculate_accesserial(location)
        # Inside Delivery: max(25, 2000 * 0.02) = max(25, 40) = 40
        assert builder._final_cost == Decimal("40")
    
    def test_weekend_cost(self):
        """주말 비용 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        # 주말(토요일) 테스트
        # 2023년 6월 3일은 토요일
        saturday = datetime.datetime(2023, 6, 3, 12, 0)
        location = QuoteLocationRequest(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=saturday,
            accessorials=[]
        )
        
        builder.calculate_service_extra_cost(False, location)
        # 주말 비용: 100
        assert builder._final_cost == Decimal("100")
        
        # 주중(수요일) 테스트
        # 2023년 6월 7일은 수요일
        wednesday = datetime.datetime(2023, 6, 7, 12, 0)
        location.request_datetime = wednesday
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_service_extra_cost(False, location)
        # 주중 비용: 0
        assert builder._final_cost == Decimal("0")
    
    def test_after_hour_cost(self):
        """영업 시간 외 비용 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        # 영업 시간 외(18시) 테스트
        after_hour = datetime.datetime(2023, 6, 7, 18, 0)  # 수요일 18시
        location = QuoteLocationRequest(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=after_hour,
            accessorials=[]
        )
        
        builder.calculate_service_extra_cost(False, location)
        # 영업 시간 외 비용: 100
        assert builder._final_cost == Decimal("100")
        
        # 영업 시간 내(14시) 테스트
        business_hour = datetime.datetime(2023, 6, 7, 14, 0)  # 수요일 14시
        location.request_datetime = business_hour
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_service_extra_cost(False, location)
        # 영업 시간 내 비용: 0
        assert builder._final_cost == Decimal("0")
    
    def test_priority_cost(self):
        """우선 순위 비용 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        # 우선 순위 + 영업 시간 내 테스트
        business_hour = datetime.datetime(2023, 6, 7, 14, 0)  # 수요일 14시
        location = QuoteLocationRequest(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=business_hour,
            accessorials=[]
        )
        
        builder.calculate_service_extra_cost(True, location)
        # 우선 순위 + 영업 시간 내 비용: 100
        assert builder._final_cost == Decimal("100")
        
        # 우선 순위 + 영업 시간 외 테스트
        after_hour = datetime.datetime(2023, 6, 7, 18, 0)  # 수요일 18시
        location.request_datetime = after_hour
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_service_extra_cost(True, location)
        # 우선 순위 + 영업 시간 외 비용: 100 (영업 시간 외 비용만)
        assert builder._final_cost == Decimal("100")
        
        # 우선 순위 없음 + 영업 시간 내 테스트
        location.request_datetime = business_hour
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_service_extra_cost(False, location)
        # 우선 순위 없음 + 영업 시간 내 비용: 0
        assert builder._final_cost == Decimal("0")
    
    def test_combined_costs(self):
        """모든 비용 조합 테스트"""
        base_cost = BaseCost(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        # 부가 서비스 + 주말 + 우선 순위 조합 테스트
        saturday = datetime.datetime(2023, 6, 3, 12, 0)  # 토요일 12시
        location = QuoteLocationRequest(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=saturday,
            accessorials=[
                QuoteLocationAccessorialRequest(
                    cargo_accessorial_id=1,
                    name="Inside Delivery"
                ),
                QuoteLocationAccessorialRequest(
                    cargo_accessorial_id=3,
                    name="Lift Gate"
                )
            ]
        )
        
        # 부가 서비스 계산
        builder.calculate_accesserial(location)
        # Inside Delivery + Lift Gate = 25 + 25 = 50
        
        # 서비스 추가 비용 계산
        builder.calculate_service_extra_cost(True, location)
        # 주말 비용 + 우선 순위(업무 시간) = 100 + 100 = 200
        
        # 총 비용: 50 + 200 = 250
        assert builder._final_cost == Decimal("250")
        
        # 결과 계산
        result = builder.calculate()
        assert result.cost == Decimal("250") 