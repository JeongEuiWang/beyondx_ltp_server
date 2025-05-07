from fastapi import APIRouter, Query, status
from pydantic import EmailStr
from typing import List

from ..core.auth import requiredAuthDeps
from ..core.exceptions import ValidationException
from ..schema.user import (
    CreateUserRequest,
    CreateUserResponse,
    CheckEmailResponse,
    GetUserInfoResponse,
    CreateUserAddressRequest,
    CreateUserAddressResponse,
    GetUserAddressResponse,
)

from ..service._deps import (
    userServiceDeps,
)

router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    "/check-email", response_model=CheckEmailResponse, status_code=status.HTTP_200_OK
)
async def check_email(
    user_service: userServiceDeps,
    email: EmailStr = Query(..., description="이메일"),
):
    result = await user_service.check_email(email)
    if not result.is_unique:
        raise ValidationException(
            message="이미 사용 중인 이메일입니다", details={"is_unique": False}
        )
    return result


@router.post(
    "/sign-up", response_model=CreateUserResponse, status_code=status.HTTP_200_OK
)
async def sign_up(user_data: CreateUserRequest, user_service: userServiceDeps):
    return await user_service.create_user(user_data)


@router.get("/me", response_model=GetUserInfoResponse, status_code=status.HTTP_200_OK)
async def get_user_info(user_service: userServiceDeps, token_data: requiredAuthDeps):
    return await user_service.get_user_info(token_data.user_id)


@router.post(
    "/address", response_model=CreateUserAddressResponse, status_code=status.HTTP_200_OK
)
async def create_user_address(
    address_data: CreateUserAddressRequest,
    user_service: userServiceDeps,
    token_data: requiredAuthDeps,
):
    return await user_service.create_user_address(token_data.user_id, address_data)


@router.get(
    "/address",
    response_model=List[GetUserAddressResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_address(user_service: userServiceDeps, token_data: requiredAuthDeps):
    return await user_service.get_user_addresses(token_data.user_id)
