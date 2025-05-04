"""
운임(Rate) API 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestRateAPI:
    """운임 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_get_locations_by_region_id(self, client: AsyncClient):
        """지역 ID로 위치 목록 조회 테스트"""
        # 지역 ID로 위치 조회 - 실제 데이터는 DB에 따라 다를 수 있음
        # 여기서는 region_id=1로 테스트
        region_id = 1
        response = await client.get(f"/api/rate/location/{region_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # 데이터가 있는지 확인은 DB 상태에 따라 다를 수 있으므로,
        # 응답 형식이 올바른지만 확인
        if data:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "city" in data[0]
            assert "zip_code" in data[0]
    
    @pytest.mark.asyncio
    async def test_get_locations_by_city(self, client: AsyncClient):
        """도시명으로 위치 목록 필터링 테스트"""
        region_id = 1
        city = "TestCity"  # 테스트용 도시명
        response = await client.get(f"/api/rate/location/{region_id}?city={city}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # 필터링 결과가 올바른지 확인
        # 데이터가 있을 경우만 검증 
        if data:
            for location in data:
                assert location["city"] == city
    
    @pytest.mark.asyncio
    async def test_get_locations_by_zip_code(self, client: AsyncClient):
        """우편번호로 위치 목록 필터링 테스트"""
        region_id = 1
        zip_code = "12345"  # 테스트용 우편번호
        response = await client.get(f"/api/rate/location/{region_id}?zip_code={zip_code}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # 필터링 결과가 올바른지 확인
        # 데이터가 있을 경우만 검증
        if data:
            for location in data:
                assert location["zip_code"] == zip_code 