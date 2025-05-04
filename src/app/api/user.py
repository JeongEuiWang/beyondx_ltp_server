from fastapi import APIRouter, Query, HTTPException, status, Depends
from pydantic import EmailStr
from typing import List

from app.core.auth import requiredAuthDeps
from app.schema.user_level import UserLevelResponse

from ..schema.user import (
    CreateUserRequest,
    CreateUserResponse,
    CheckEmailResponse,
    GetUserInfoResponse,
)

from ..schema.user_address import (
    CreateUserAddressRequest,
    CreateUserAddressResponse,
    UserAddressResponse,
)
from ..service._deps import (
    userServiceDeps,
    userAddressServiceDeps,
    userLevelServiceDeps,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"is_unique": False}
        )
    return result


@router.post(
    "/sign-up", response_model=CreateUserResponse, status_code=status.HTTP_200_OK
)
async def sign_up(user_data: CreateUserRequest, user_service: userServiceDeps):
    return await user_service.create_user(user_data)


@router.get("/", response_model=GetUserInfoResponse, status_code=status.HTTP_200_OK)
async def get_user_info(user_service: userServiceDeps, token_data: requiredAuthDeps):
    return await user_service.get_user_info(token_data.user_id)


@router.post(
    "/address", response_model=CreateUserAddressResponse, status_code=status.HTTP_200_OK
)
async def create_user_address(
    address_data: CreateUserAddressRequest,
    user_address_service: userAddressServiceDeps,
    token_data: requiredAuthDeps,
):
    return await user_address_service.create_user_address(
        token_data.user_id, address_data
    )


@router.get(
    "/address",
    response_model=List[UserAddressResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_address(
    user_address_service: userAddressServiceDeps, token_data: requiredAuthDeps
):
    return await user_address_service.get_user_addresses(token_data.user_id)


@router.get(
    "/levels",
    response_model=List[UserLevelResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_level(user_level_service: userLevelServiceDeps):
    return await user_level_service.get_user_levels()
