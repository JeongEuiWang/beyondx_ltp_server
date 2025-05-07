from fastapi import APIRouter, Query, status
from pydantic import EmailStr
from typing import List

from ..core.auth import TokenData
from ..service import UserService
from ..core.dependencies import container
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

router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    "/check-email", response_model=CheckEmailResponse, status_code=status.HTTP_200_OK
)
async def check_email(
    user_service: UserService = container.get("user_service"),
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
async def sign_up(
    user_data: CreateUserRequest,
    user_service: UserService = container.get("user_service"),
):
    return await user_service.create_user(user_data)


@router.get("/me", response_model=GetUserInfoResponse, status_code=status.HTTP_200_OK)
async def get_user_info(
    user_service: UserService = container.get("user_service"),
    token_data: TokenData = container.get("required_authorization"),
):
    return await user_service.get_user_info(token_data.user_id)


@router.post(
    "/address", response_model=CreateUserAddressResponse, status_code=status.HTTP_200_OK
)
async def create_user_address(
    address_data: CreateUserAddressRequest,
    user_service: UserService = container.get("user_service"),
    token_data: TokenData = container.get("required_authorization"),
):
    return await user_service.create_user_address(token_data.user_id, address_data)


@router.get(
    "/address",
    response_model=List[GetUserAddressResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_address(
    user_service: UserService = container.get("user_service"),
    token_data: TokenData = container.get("required_authorization"),
):
    return await user_service.get_user_addresses(token_data.user_id)
