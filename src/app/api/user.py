from fastapi import APIRouter, Query, status, Depends
from pydantic import EmailStr
from typing import List

from ..core.auth import TokenData
from ..service import UserService
from ..core.uow import get_uow
from ..db.unit_of_work import UnitOfWork
from ..schema.user import (
    CreateUserRequest,
    CreateUserResponse,
    CheckEmailResponse,
    GetUserInfoResponse,
    CreateUserAddressRequest,
    CreateUserAddressResponse,
    GetUserAddressResponse,
    UpdateUserAddressRequest,
    UpdateUserAddressResponse,
    DeleteUserAddressResponse,
)
from ..core.auth import required_authorization

router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    "/check-email", response_model=CheckEmailResponse, status_code=status.HTTP_200_OK
)
async def check_email(
    email: EmailStr = Query(..., description="Email"),
    uow: UnitOfWork = Depends(get_uow),
):
    user_service = UserService(uow)
    return await user_service.check_email(email=email)


@router.post("", response_model=CreateUserResponse, status_code=status.HTTP_200_OK)
async def create_user(
    request: CreateUserRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    user_service = UserService(uow)
    return await user_service.create_user(request=request)


@router.get("/me", response_model=GetUserInfoResponse, status_code=status.HTTP_200_OK)
async def get_user_info(
    token_data: TokenData = Depends(required_authorization),
    uow: UnitOfWork = Depends(get_uow),
):
    user_service = UserService(uow)
    return await user_service.get_user_info(token_data.user_id)


@router.post(
    "/address", response_model=CreateUserAddressResponse, status_code=status.HTTP_200_OK
)
async def create_user_address(
    request: CreateUserAddressRequest,
    token_data: TokenData = Depends(required_authorization),
    uow: UnitOfWork = Depends(get_uow),
):
    user_service = UserService(uow)
    return await user_service.create_user_address(token_data.user_id, request=request)


@router.get(
    "/address",
    response_model=List[GetUserAddressResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_address(
    token_data: TokenData = Depends(required_authorization),
    uow: UnitOfWork = Depends(get_uow),
):
    user_service = UserService(uow)
    return await user_service.get_user_addresses(token_data.user_id)


@router.put(
    "/address/{address_id}",
    response_model=UpdateUserAddressResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user_address(
    address_id: int,
    request: UpdateUserAddressRequest,
    token_data: TokenData = Depends(required_authorization),
    uow: UnitOfWork = Depends(get_uow),
):
    user_service = UserService(uow)
    return await user_service.update_user_address(
        token_data.user_id, address_id, request=request
    )


@router.delete(
    "/address/{address_id}",
    response_model=DeleteUserAddressResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_user_address(
    address_id: int,
    token_data: TokenData = Depends(required_authorization),
    uow: UnitOfWork = Depends(get_uow),
):
    user_service = UserService(uow)
    return await user_service.delete_user_address(token_data.user_id, address_id)
