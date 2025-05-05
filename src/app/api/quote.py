from fastapi import APIRouter, Query, Depends, status, Path
from typing import Optional, List
from app.core.auth import requiredAuthDeps
from app.service._deps import (
    quoteServiceDeps,
    costServiceDeps,
)
from app.schema.quote import CreateQuoteRequest

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
    location_type_cost = await cost_service.calculate_location_type_cost(
        request.from_location, request.to_location, base_cost
    )
    extra_cost = await cost_service.calculate_extra_cost(
        request.is_priority, request.from_location, request.to_location, base_cost
    )
    total_cost = base_cost.cost + location_type_cost.cost + extra_cost.cost
    discount_cost = await cost_service.calculate_discount(
        token_data.user_id, total_cost
    )
    return await quote_service.create_quote(
        user_id=token_data.user_id,
        quote=request,
        total_weight=base_cost.freight_weight,
        total_cost=discount_cost,
    )
