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
        return ErrorDetail(
            code=self.code,
            message=self.message,
            details=self.details
        )

class AuthException(AppException):
    def __init__(
        self,
        code: str = "UNAUTHORIZED",
        message: str = "Authentication failed",
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
        message: str = "This operation is forbidden",
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
        code: str = "NOT_FOUND",
        message: str = "Not found",
        details: Optional[Dict[str, Any]] = None
    ):
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
        message: str = "Invalid input data",
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
        message: str = "Bad request",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )