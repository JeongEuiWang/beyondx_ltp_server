from fastapi import APIRouter, Query, status, Path, Depends, Request
from typing import List, Optional

from ..core.exceptions import BadRequestException, NotFoundException
from ..core.uow import get_uow
from ..db.unit_of_work import UnitOfWork
from ..core.auth import TokenData
from ..service import CostService, QuoteService
from ..schema.quote import (
    CreateQuoteRequest,
    UpdateQuoteRequest,
    GetQuotesResponse,
    GetQuoteDetailsResponse,
    ConfirmQuoteRequest,
)
from ..schema._common import BaseQuoteSchema
from ..core.auth import required_authorization

router = APIRouter(prefix="/quote", tags=["quote"])


@router.get(
    "",
    response_model=list[GetQuotesResponse],
    status_code=status.HTTP_200_OK,
)
async def get_quotes(
    uow: UnitOfWork = Depends(get_uow),
    token_data: TokenData = Depends(required_authorization),
):
    quote_service = QuoteService(uow)
    return await quote_service.get_quotes(token_data.user_id)


@router.get(
    "/admin",
    response_model=list[GetQuotesResponse],
    status_code=status.HTTP_200_OK,
)
async def get_quotes_admin(
    request: Request,
    uow: UnitOfWork = Depends(get_uow),
    token_data: TokenData = Depends(required_authorization),
):
    status_values = []
    query_params = request.query_params
    
    for key, value in query_params.items():
        if key.startswith('status[') and key.endswith(']'):
            status_values.append(value)
        elif key == 'status':
            if isinstance(query_params.getlist('status'), list):
                status_values.extend(query_params.getlist('status'))
            else:
                status_values.append(value)
    
    quote_service = QuoteService(uow)
    return await quote_service.get_quotes_admin(token_data.role_id, status_values)


@router.get(
    "/admin/{quote_id}",
    response_model=list[GetQuotesResponse],
    status_code=status.HTTP_200_OK,
)
async def get_quote_details_admin(
    uow: UnitOfWork = Depends(get_uow),
    quote_id: str = Path(..., description="Quote ID"),
    token_data: TokenData = Depends(required_authorization),
):
    quote_service = QuoteService(uow)
    return await quote_service.get_quote_by_id(quote_id, token_data)


@router.get(
    "/{quote_id}",
    response_model=GetQuoteDetailsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_quote_details(
    quote_id: str = Path(..., description="인용 ID"),
    uow: UnitOfWork = Depends(get_uow),
    token_data: TokenData = Depends(required_authorization),
):
    quote_service = QuoteService(uow)
    return await quote_service.get_quote_by_id(quote_id, token_data)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=BaseQuoteSchema,
)
async def create_quote(
    request: CreateQuoteRequest,
    uow: UnitOfWork = Depends(get_uow),
    token_data: TokenData = Depends(required_authorization),
):
    cost_service = CostService(uow)
    quote_service = QuoteService(uow)

    base_cost = await cost_service.calculate_base_cost(
        cargo_transportation_id=request.cargo_transportation_id,
        cargo_list=request.cargo,
        from_location=request.from_location,
        to_location=request.to_location,
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
        quote_data=request,
        total_weight=base_cost.freight_weight,
        base_price=base_price,
        extra_price=extra_price,
        total_price_with_discount=total_price_with_discount.cost,
    )


@router.put(
    "/{quote_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetQuoteDetailsResponse,
)
async def update_quote(
    request: UpdateQuoteRequest,
    quote_id: str = Path(..., description="인용 ID"),
    uow: UnitOfWork = Depends(get_uow),
    token_data: TokenData = Depends(required_authorization),
):
    cost_service = CostService(uow)
    quote_service = QuoteService(uow)

    base_cost = await cost_service.calculate_base_cost(
        cargo_transportation_id=request.cargo_transportation_id,
        cargo_list=request.cargo,
        from_location=request.from_location,
        to_location=request.to_location,
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

    return await quote_service.update_quote(
        quote_id=quote_id,
        user_id=token_data.user_id,
        quote_data=request,
        total_weight=base_cost.freight_weight,
        base_price=base_price,
        extra_price=extra_price,
        total_price_with_discount=total_price_with_discount.cost,
    )


@router.post(
    "/{quote_id}/submit",
    status_code=status.HTTP_200_OK,
    response_model=GetQuoteDetailsResponse,
)
async def submit_quote(
    uow: UnitOfWork = Depends(get_uow),
    token_data: TokenData = Depends(required_authorization),
    quote_id: str = Path(..., description="인용 ID"),
):
    quote_service = QuoteService(uow)
    return await quote_service.submit_quote(quote_id, token_data.user_id, token_data)


@router.post(
    "/{quote_id}/confirm",
    status_code=status.HTTP_200_OK,
    response_model=GetQuoteDetailsResponse,
)
async def confirm_quote(
    request: ConfirmQuoteRequest,
    uow: UnitOfWork = Depends(get_uow),
    token_data: TokenData = Depends(required_authorization),
    quote_id: str = Path(..., description="인용 ID"),
):
    quote_service = QuoteService(uow)
    return await quote_service.confirm_quote(quote_id, token_data.role_id, request, token_data)
