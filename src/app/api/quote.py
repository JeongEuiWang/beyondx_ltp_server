from typing import List
from fastapi import APIRouter, HTTPException, status, Path

from ..core.exceptions import BadRequestException, NotFoundException
from ..core.auth import requiredAuthDeps
from ..service._deps import (
    quoteServiceDeps,
    costServiceDeps,
)
from ..schema.quote import (
    CreateQuoteRequest,
    UpdateQuoteRequest,
    GetQuotesResponse,
    GetQuoteDetailsResponse,
)

router = APIRouter(prefix="/quote", tags=["quote"])


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
async def create_quote(
    cost_service: costServiceDeps,
    quote_service: quoteServiceDeps,
    token_data: requiredAuthDeps,
    request: CreateQuoteRequest,
):
    base_cost = await cost_service.calculate_base_cost(
        request.cargo, request.from_location, request.to_location
    )

    if base_cost.is_max_load:
        raise BadRequestException(
            message="최대 금액을 초과했습니다. 고객사에 직접 문의해주세요.",
        )

    location_type_cost = await cost_service.calculate_location_type_cost(
        request.from_location, request.to_location, base_cost
    )
    extra_cost = await cost_service.calculate_extra_cost(
        request.is_priority, request.from_location, request.to_location, base_cost
    )

    total_price = base_cost.cost + location_type_cost.cost + extra_cost.cost
    base_price = base_cost.cost
    extra_price = location_type_cost.cost + extra_cost.cost

    total_price_with_discount = await cost_service.calculate_discount(
        token_data.user_id, total_price
    )
    return await quote_service.create_quote(
        user_id=token_data.user_id,
        quote=request,
        total_weight=base_cost.freight_weight,
        base_price=base_price,
        extra_price=extra_price,
        total_price_with_discount=total_price_with_discount.cost,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[GetQuotesResponse],
)
async def get_quotes(
    quote_service: quoteServiceDeps,
    token_data: requiredAuthDeps,
):
    return await quote_service.get_quotes(token_data.user_id)


@router.get(
    "/{quote_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetQuoteDetailsResponse,
)
async def get_quote_details(
    quote_service: quoteServiceDeps,
    token_data: requiredAuthDeps,
    quote_id: str = Path(..., description="인용 ID"),
):
    return await quote_service.get_quote_by_id(quote_id, token_data.user_id)


@router.put(
    "/{quote_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
async def update_quote(
    cost_service: costServiceDeps,
    quote_service: quoteServiceDeps,
    token_data: requiredAuthDeps,
    request: UpdateQuoteRequest,
    quote_id: str = Path(..., description="인용 ID"),
):
    # 기존 견적 조회
    quote = await quote_service.get_quote_by_id(quote_id, token_data.user_id)
    if not quote:
        raise NotFoundException(
            message="해당 견적을 찾을 수 없습니다.",
        )

    # 비용 재계산 - 클라이언트에서 모든 정보를 포함해서 보내므로 바로 계산할 수 있음
    base_cost = await cost_service.calculate_base_cost(
        request.cargo, request.from_location, request.to_location
    )

    if base_cost.is_max_load:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최대 금액을 초과했습니다. 고객사에 직접 문의해주세요.",
        )

    location_type_cost = await cost_service.calculate_location_type_cost(
        request.from_location, request.to_location, base_cost
    )
    extra_cost = await cost_service.calculate_extra_cost(
        request.is_priority, request.from_location, request.to_location, base_cost
    )

    total_price = base_cost.cost + location_type_cost.cost + extra_cost.cost
    base_price = base_cost.cost
    extra_price = location_type_cost.cost + extra_cost.cost
    total_price_with_discount = await cost_service.calculate_discount(
        token_data.user_id, total_price
    )

    # 견적 업데이트
    return await quote_service.update_quote(
        quote_id=quote_id,
        user_id=token_data.user_id,
        quote=request,
        total_weight=base_cost.freight_weight,
        base_price=base_price,
        extra_price=extra_price,
        total_price_with_discount=total_price_with_discount.cost,
    )

@router.post(
    "/{quote_id}/submit",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
async def submit_quote(
    quote_service: quoteServiceDeps,
    token_data: requiredAuthDeps,
    quote_id: str = Path(..., description="인용 ID"),
):
    return await quote_service.submit_quote(quote_id, token_data.user_id)