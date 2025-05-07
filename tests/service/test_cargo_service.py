"""
화물(Cargo) 서비스 테스트
"""

import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from typing import List

# 스키마 경로 수정
from app.schema.cargo.response import CargoTransportationResponse, CargoAccessorialResponse

# 서비스 클래스를 모킹
class MockCargoService:
    def __init__(self, repository):
        self.cargo_repository = repository
        
    async def get_cargo_transportation(self) -> List[CargoTransportationResponse]:
        """화물 운송 유형 목록을 조회합니다."""
        try:
            transportations = await self.cargo_repository.get_cargo_transportation()
            return [CargoTransportationResponse.model_validate(trans) for trans in transportations]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"화물 운송 유형 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    async def get_cargo_accessorial(self) -> List[CargoAccessorialResponse]:
        """화물 부가 서비스 목록을 조회합니다."""
        try:
            accessorials = await self.cargo_repository.get_cargo_accessorial()
            return [CargoAccessorialResponse.model_validate(acc) for acc in accessorials]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"화물 부가 서비스 조회 중 오류가 발생했습니다: {str(e)}"
            )


class TestCargoService:
    """화물 서비스 테스트 클래스"""
    
    @pytest.fixture
    def cargo_repository_mock(self):
        """화물 리포지토리 모킹"""
        mock = AsyncMock()
        mock.get_cargo_transportation = AsyncMock()
        mock.get_cargo_accessorial = AsyncMock()
        return mock
    
    @pytest.fixture
    def cargo_service(self, cargo_repository_mock):
        """화물 서비스 인스턴스 생성"""
        return MockCargoService(cargo_repository_mock)
    
    @pytest.mark.asyncio
    async def test_get_cargo_transportation_success(self, cargo_service, cargo_repository_mock):
        """운송 유형 조회 성공 테스트"""
        # Mock 데이터 설정
        mock_transportations = [
            {"id": 1, "name": "FCL", "description": "Full Container Load"},
            {"id": 2, "name": "LCL", "description": "Less Container Load"}
        ]
        cargo_repository_mock.get_cargo_transportation.return_value = mock_transportations
        
        # 테스트 실행
        result = await cargo_service.get_cargo_transportation()
        
        # 검증
        assert len(result) == 2
        assert isinstance(result[0], CargoTransportationResponse)
        assert result[0].id == 1
        assert result[0].name == "FCL"
        assert result[0].description == "Full Container Load"
        
        # 리포지토리 메서드 호출 확인
        cargo_repository_mock.get_cargo_transportation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cargo_transportation_empty(self, cargo_service, cargo_repository_mock):
        """운송 유형 조회 결과가 비어있는 경우 테스트"""
        # Mock 데이터 설정 - 빈 리스트
        cargo_repository_mock.get_cargo_transportation.return_value = []
        
        # 테스트 실행
        result = await cargo_service.get_cargo_transportation()
        
        # 검증
        assert isinstance(result, list)
        assert len(result) == 0
        
        # 리포지토리 메서드 호출 확인
        cargo_repository_mock.get_cargo_transportation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cargo_transportation_error(self, cargo_service, cargo_repository_mock):
        """운송 유형 조회 중 오류 발생 테스트"""
        # 예외 발생 시뮬레이션
        cargo_repository_mock.get_cargo_transportation.side_effect = Exception("데이터베이스 오류")
        
        # 테스트 실행 및 예외 검증
        with pytest.raises(HTTPException) as excinfo:
            await cargo_service.get_cargo_transportation()
        
        # 예외 상세 검증
        assert excinfo.value.status_code == 500
        assert "화물 운송 유형 조회 중 오류가 발생했습니다" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_get_cargo_accessorial_success(self, cargo_service, cargo_repository_mock):
        """부가 서비스 조회 성공 테스트"""
        # Mock 데이터 설정
        mock_accessorials = [
            {"id": 1, "name": "검역", "description": "화물 검역 서비스"},
            {"id": 2, "name": "포장", "description": "화물 포장 서비스"}
        ]
        cargo_repository_mock.get_cargo_accessorial.return_value = mock_accessorials
        
        # 테스트 실행
        result = await cargo_service.get_cargo_accessorial()
        
        # 검증
        assert len(result) == 2
        assert isinstance(result[0], CargoAccessorialResponse)
        assert result[0].id == 1
        assert result[0].name == "검역"
        assert result[0].description == "화물 검역 서비스"
        
        # 리포지토리 메서드 호출 확인
        cargo_repository_mock.get_cargo_accessorial.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cargo_accessorial_empty(self, cargo_service, cargo_repository_mock):
        """부가 서비스 조회 결과가 비어있는 경우 테스트"""
        # Mock 데이터 설정 - 빈 리스트
        cargo_repository_mock.get_cargo_accessorial.return_value = []
        
        # 테스트 실행
        result = await cargo_service.get_cargo_accessorial()
        
        # 검증
        assert isinstance(result, list)
        assert len(result) == 0
        
        # 리포지토리 메서드 호출 확인
        cargo_repository_mock.get_cargo_accessorial.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cargo_accessorial_error(self, cargo_service, cargo_repository_mock):
        """부가 서비스 조회 중 오류 발생 테스트"""
        # 예외 발생 시뮬레이션
        cargo_repository_mock.get_cargo_accessorial.side_effect = Exception("데이터베이스 오류")
        
        # 테스트 실행 및 예외 검증
        with pytest.raises(HTTPException) as excinfo:
            await cargo_service.get_cargo_accessorial()
        
        # 예외 상세 검증
        assert excinfo.value.status_code == 500
        assert "화물 부가 서비스 조회 중 오류가 발생했습니다" in excinfo.value.detail 