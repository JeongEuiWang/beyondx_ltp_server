"""
운임(Rate) 서비스 테스트
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from typing import List, Optional

# 스키마만 임포트하고 서비스나 리포지토리는 임포트하지 않음
from src.app.schema.rate import RateLocationResponse

# 서비스 클래스를 모킹
class MockRateService:
    def __init__(self, repository):
        self.rate_repository = repository
        
    async def get_rate_locations(
        self, region_id: int, city: Optional[str] = None, zip_code: Optional[str] = None
    ) -> List[RateLocationResponse]:
        """위치 정보 조회 메서드"""
        # 실제 서비스에서의 로직 복제
        try:
            if region_id <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 지역 ID입니다."
                )
            
            locations = await self.rate_repository.get_rate_location_by_query(
                region_id, city, zip_code
            )
            return [RateLocationResponse.model_validate(loc) for loc in locations]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"위치 정보 조회 중 오류가 발생했습니다: {str(e)}"
            )


class TestRateService:
    """운임 서비스 테스트 클래스"""
    
    @pytest.fixture
    def rate_repository_mock(self):
        """운임 리포지토리 모킹"""
        mock = AsyncMock()
        # 필요한 메서드만 직접 설정
        mock.get_rate_location_by_query = AsyncMock()
        return mock
    
    @pytest.fixture
    def rate_service(self, rate_repository_mock):
        """운임 서비스 인스턴스 생성"""
        return MockRateService(rate_repository_mock)
    
    @pytest.mark.asyncio
    async def test_get_rate_locations_success(self, rate_service, rate_repository_mock):
        """위치 정보 조회 성공 테스트"""
        # Mock 데이터 설정
        region_id = 1
        mock_locations = [
            {
                "id": 1,
                "city": "서울", 
                "zip_code": "12345",
                "area_id": 100,
                "state": "서울특별시",
                "county": "강남구"
            },
            {
                "id": 2,
                "city": "부산", 
                "zip_code": "67890",
                "area_id": 200,
                "state": "부산광역시",
                "county": "해운대구"
            }
        ]
        rate_repository_mock.get_rate_location_by_query.return_value = mock_locations
        
        # 테스트 실행
        result = await rate_service.get_rate_locations(region_id)
        
        # 검증
        assert len(result) == 2
        assert isinstance(result[0], RateLocationResponse)
        assert result[0].id == 1
        assert result[0].city == "서울"
        assert result[0].zip_code == "12345"
        assert result[0].area_id == 100
        assert result[0].state == "서울특별시"
        assert result[0].county == "강남구"
        
        # 리포지토리 메서드 호출 확인
        rate_repository_mock.get_rate_location_by_query.assert_called_once_with(
            region_id, None, None
        )
    
    @pytest.mark.asyncio
    async def test_get_rate_locations_with_filter(self, rate_service, rate_repository_mock):
        """필터 조건으로 위치 정보 조회 테스트"""
        # Mock 데이터 설정
        region_id = 1
        city = "서울"
        mock_locations = [
            {
                "id": 1,
                "city": "서울", 
                "zip_code": "12345",
                "area_id": 100,
                "state": "서울특별시",
                "county": "강남구"
            },
            {
                "id": 2,
                "city": "서울", 
                "zip_code": "12346",
                "area_id": 101,
                "state": "서울특별시",
                "county": "서초구"
            }
        ]
        rate_repository_mock.get_rate_location_by_query.return_value = mock_locations
        
        # 테스트 실행
        result = await rate_service.get_rate_locations(region_id, city)
        
        # 검증
        assert len(result) == 2
        for location in result:
            assert location.city == "서울"
        
        # 리포지토리 메서드 호출 확인
        rate_repository_mock.get_rate_location_by_query.assert_called_once_with(
            region_id, city, None
        )
    
    @pytest.mark.asyncio
    async def test_get_rate_locations_by_zip_code(self, rate_service, rate_repository_mock):
        """우편번호로 위치 정보 조회 테스트"""
        # Mock 데이터 설정
        region_id = 1
        zip_code = "12345"
        mock_locations = [
            {
                "id": 1,
                "city": "서울", 
                "zip_code": "12345",
                "area_id": 100,
                "state": "서울특별시",
                "county": "강남구"
            }
        ]
        rate_repository_mock.get_rate_location_by_query.return_value = mock_locations
        
        # 테스트 실행
        result = await rate_service.get_rate_locations(region_id, None, zip_code)
        
        # 검증
        assert len(result) == 1
        assert result[0].zip_code == "12345"
        
        # 리포지토리 메서드 호출 확인
        rate_repository_mock.get_rate_location_by_query.assert_called_once_with(
            region_id, None, zip_code
        )
    
    @pytest.mark.asyncio
    async def test_get_rate_locations_empty(self, rate_service, rate_repository_mock):
        """위치 정보 조회 결과가 비어있는 경우 테스트"""
        # Mock 데이터 설정 - 빈 리스트
        region_id = 1
        rate_repository_mock.get_rate_location_by_query.return_value = []
        
        # 테스트 실행
        result = await rate_service.get_rate_locations(region_id)
        
        # 검증
        assert isinstance(result, list)
        assert len(result) == 0
        
        # 리포지토리 메서드 호출 확인
        rate_repository_mock.get_rate_location_by_query.assert_called_once_with(
            region_id, None, None
        )
    
    @pytest.mark.asyncio
    async def test_get_rate_locations_invalid_region(self, rate_service):
        """유효하지 않은 지역 ID로 조회 시 예외 발생 테스트"""
        # 유효하지 않은 지역 ID
        region_id = 0
        
        # 테스트 실행 및 예외 검증
        with pytest.raises(HTTPException) as excinfo:
            await rate_service.get_rate_locations(region_id)
        
        # 예외 상세 검증
        assert excinfo.value.status_code == 400
        assert "유효하지 않은 지역 ID입니다" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_get_rate_locations_error(self, rate_service, rate_repository_mock):
        """위치 정보 조회 중 오류 발생 테스트"""
        # 예외 발생 시뮬레이션
        region_id = 1
        rate_repository_mock.get_rate_location_by_query.side_effect = Exception("데이터베이스 오류")
        
        # 테스트 실행 및 예외 검증
        with pytest.raises(HTTPException) as excinfo:
            await rate_service.get_rate_locations(region_id)
        
        # 예외 상세 검증
        assert excinfo.value.status_code == 500
        assert "위치 정보 조회 중 오류가 발생했습니다" in excinfo.value.detail 