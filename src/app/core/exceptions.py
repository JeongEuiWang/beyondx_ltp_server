# src/app/core/exceptions.py
from typing import Any, Dict, Optional, Union
from fastapi import status
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)
    
    def to_error_detail(self) -> ErrorDetail:
        """ErrorDetail 모델로 변환"""
        return ErrorDetail(
            code=self.code,
            message=self.message,
            details=self.details
        )

class AuthException(AppException):
    def __init__(
        self,
        code: str = "UNAUTHORIZED",
        message: str = "인증에 실패했습니다",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )

class ForbiddenException(AppException):
    def __init__(
        self,
        code: str = "FORBIDDEN",
        message: str = "이 작업을 수행할 권한이 없습니다",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )

class NotFoundException(AppException):
    def __init__(
        self,
        entity: str,
        entity_id: Union[str, int],
        code: str = "NOT_FOUND",
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if message is None:
            message = f"{entity}(id: {entity_id})를 찾을 수 없습니다"
        
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )

class ValidationException(AppException):
    def __init__(
        self,
        code: str = "VALIDATION_ERROR",
        message: str = "입력 데이터가 유효하지 않습니다",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )

class BadRequestException(AppException):
    def __init__(
        self,
        code: str = "BAD_REQUEST",
        message: str = "잘못된 요청입니다",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )