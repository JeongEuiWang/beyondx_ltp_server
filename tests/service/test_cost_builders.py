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
from app.schema.cost.response import BaseCostSchema
from app.schema._common import QuoteLocationSchema
from app.schema._common import QuoteLocationAccessorialSchema
from app.model._enum import LocationTypeEnum

class RateCost:
    def __init__(self, min_weight, max_weight, price_per_weight):
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.price_per_weight = price_per_weight


class TestBaseCostBuilder:
    """BaseCostBuilder 테스트 클래스"""

    def test_set_freight_weight(self):
        """화물 무게 계산 테스트"""
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        
        builder.set_freight_weight(weight=50, quantity=2, width=10, height=10, length=10)
        assert builder._freight_weight == Decimal("100")
        
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder.set_freight_weight(weight=1, quantity=1, width=100, height=100, length=100)
        assert builder._freight_weight == Decimal("6024.097")
    
    def test_set_price_per_weight(self):
        """가격/무게 비율 계산 테스트"""
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_weight = Decimal("100")
        builder._max_load_weight = Decimal("200")
        
        rate_costs = [
            RateCost(min_weight=Decimal("0"), max_weight=Decimal("50"), price_per_weight=Decimal("5")),
            RateCost(min_weight=Decimal("51"), max_weight=Decimal("150"), price_per_weight=Decimal("4")),
            RateCost(min_weight=Decimal("151"), max_weight=Decimal("500"), price_per_weight=Decimal("3"))
        ]
        
        builder.set_price_per_weight(rate_costs)
        assert builder._price_per_weight == Decimal("4")
        
        builder._freight_weight = Decimal("1000")
        builder._max_load_weight = Decimal("1500")
        builder.set_price_per_weight(rate_costs)
        assert builder._price_per_weight == Decimal("4")
    
    def test_set_price_per_weight_exceeds_max_weight(self):
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        
        builder._freight_weight = Decimal("1000")
        builder._max_load_weight = Decimal("500")
        
        rate_costs = [
            RateCost(min_weight=Decimal("0"), max_weight=Decimal("1000"), price_per_weight=Decimal("10"))
        ]
        
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
        
        builder.calculate_base_cost()
        assert builder._freight_cost == Decimal("500")
        assert builder._is_max_load == False
        
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_weight = Decimal("50")
        builder._price_per_weight = Decimal("5")
        builder._min_load = Decimal("400")
        builder._max_load = Decimal("800")
        
        builder.calculate_base_cost()
        assert builder._freight_cost == Decimal("400")
        assert builder._is_max_load == False
        
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_weight = Decimal("200")
        builder._price_per_weight = Decimal("5")
        builder._min_load = Decimal("400")
        builder._max_load = Decimal("800")
        
        builder.calculate_base_cost()
        assert builder._freight_cost == Decimal("800")
        assert builder._is_max_load == True
    
    def test_calculate_with_fsc(self):
        """연료 할증료 계산 테스트"""
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        builder._freight_cost = Decimal("500")
        
        builder.calculate_with_fsc()
        assert builder._final_cost == Decimal("675")
    
    def test_full_calculation(self):
        """전체 계산 프로세스 테스트"""
        builder = BaseCostBuilder(fsc=Decimal("0.35"))
        
        builder.set_freight_weight(weight=50, quantity=2, width=10, height=10, length=10)
        
        builder.set_location_rate(
            min_load=Decimal("400"), 
            max_load=Decimal("800"),
            max_load_weight=Decimal("200")
        )
        
        rate_costs = [
            RateCost(min_weight=Decimal("0"), max_weight=Decimal("50"), price_per_weight=Decimal("5")),
            RateCost(min_weight=Decimal("51"), max_weight=Decimal("150"), price_per_weight=Decimal("4")),
            RateCost(min_weight=Decimal("151"), max_weight=Decimal("500"), price_per_weight=Decimal("3"))
        ]
        builder.set_price_per_weight(rate_costs)
        
        builder.calculate_base_cost()
        
        builder.calculate_with_fsc()
        
        result = builder.calculate()
        
        assert result.freight_weight == Decimal("100")
        assert result.cost == Decimal("540")
        assert result.is_max_load == False


class TestLocationCostBuilder:
    """LocationCostBuilder 테스트 클래스"""

    def test_commercial_location(self):
        """상업 지역 비용 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.COMMERCIAL, "PICK_UP")
        
        assert builder._final_cost == Decimal("0")
        
        result = builder.calculate()
        assert result.cost == Decimal("0")
    
    def test_residential_location(self):
        """주거 지역 비용 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.RESIDENTIAL, "PICK_UP")
        
        assert builder._final_cost == Decimal("25")
        
        result = builder.calculate()
        assert result.cost == Decimal("25")
    
    def test_airport_location_pickup(self):
        """공항 픽업 비용 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.AIRPORT, "PICK_UP")
        
        assert builder._final_cost == Decimal("30")
        
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("10000"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.AIRPORT, "PICK_UP")
        
        assert builder._final_cost == Decimal("200")
    
    def test_airport_location_delivery(self):
        """공항 배송 비용 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("1000"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.AIRPORT, "DELIVERY")
        
        assert builder._final_cost == Decimal("30")
        
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("500"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.AIRPORT, "DELIVERY")
        
        assert builder._final_cost == Decimal("25")
    
    def test_multiple_location_types(self):
        """여러 위치 유형 조합 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = LocationCostBuilder(base_cost=base_cost)
        builder.check_location_type(LocationTypeEnum.RESIDENTIAL, "PICK_UP")
        builder.check_location_type(LocationTypeEnum.AIRPORT, "DELIVERY")
        
        assert builder._final_cost == Decimal("50")
        
        result = builder.calculate()
        assert result.cost == Decimal("50")


class TestExtraCostBuilder:
    """ExtraCostBuilder 테스트 클래스"""

    def test_accessorial_costs(self):
        """부가 서비스 비용 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        location = QuoteLocationSchema(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=datetime.datetime.now(),
            accessorials=[
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=1,
                    name="Inside Delivery"
                )
            ]
        )
        
        builder.calculate_accesserial(location)
        assert builder._final_cost == Decimal("25")
        
        location.accessorials.append(
            QuoteLocationAccessorialSchema(
                cargo_accessorial_id=2,
                name="Two Person"
            )
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_accesserial(location)
        assert builder._final_cost == Decimal("105")
        
        location.accessorials.append(
            QuoteLocationAccessorialSchema(
                cargo_accessorial_id=3,
                name="Lift Gate"
            )
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_accesserial(location)
        assert builder._final_cost == Decimal("130")
    
    def test_inside_delivery_weight_based(self):
        """Inside Delivery가 무게에 따라 계산되는 경우 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("2000"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        location = QuoteLocationSchema(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=datetime.datetime.now(),
            accessorials=[
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=1,
                    name="Inside Delivery"
                )
            ]
        )
        
        builder.calculate_accesserial(location)
        assert builder._final_cost == Decimal("40")
    
    def test_weekend_cost(self):
        """주말 비용 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        saturday = datetime.datetime(2023, 6, 3, 12, 0)
        location = QuoteLocationSchema(
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
        assert builder._final_cost == Decimal("100")
        
        wednesday = datetime.datetime(2023, 6, 7, 12, 0)
        location.request_datetime = wednesday
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_service_extra_cost(False, location)
        assert builder._final_cost == Decimal("0")
    
    def test_after_hour_cost(self):
        """영업 시간 외 비용 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        after_hour = datetime.datetime(2023, 6, 7, 18, 0)
        location = QuoteLocationSchema(
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
        assert builder._final_cost == Decimal("100")
        
        business_hour = datetime.datetime(2023, 6, 7, 14, 0)
        location.request_datetime = business_hour
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_service_extra_cost(False, location)
        assert builder._final_cost == Decimal("0")
    
    def test_priority_cost(self):
        """우선 순위 비용 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        business_hour = datetime.datetime(2023, 6, 7, 14, 0)
        location = QuoteLocationSchema(
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
        assert builder._final_cost == Decimal("100")
        
        after_hour = datetime.datetime(2023, 6, 7, 18, 0)
        location.request_datetime = after_hour
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_service_extra_cost(True, location)
        assert builder._final_cost == Decimal("100")
        
        location.request_datetime = business_hour
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        builder.calculate_service_extra_cost(False, location)
        assert builder._final_cost == Decimal("0")
    
    def test_combined_costs(self):
        """모든 비용 조합 테스트"""
        base_cost = BaseCostSchema(
            cost=Decimal("500"),
            freight_weight=Decimal("100"),
            is_max_load=False
        )
        
        builder = ExtraCostBuilder(base_cost=base_cost)
        
        saturday = datetime.datetime(2023, 6, 3, 12, 0)
        location = QuoteLocationSchema(
            state="뉴욕",
            county="뉴욕",
            city="뉴욕시",
            zip_code="10001",
            address="123 메인 스트리트",
            location_type=LocationTypeEnum.COMMERCIAL,
            request_datetime=saturday,
            accessorials=[
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=1,
                    name="Inside Delivery"
                ),
                QuoteLocationAccessorialSchema(
                    cargo_accessorial_id=3,
                    name="Lift Gate"
                )
            ]
        )
        
        builder.calculate_accesserial(location)
        
        builder.calculate_service_extra_cost(True, location)
        
        assert builder._final_cost == Decimal("250")
        
        result = builder.calculate()
        assert result.cost == Decimal("250") 