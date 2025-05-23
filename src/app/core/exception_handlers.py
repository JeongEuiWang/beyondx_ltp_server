from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.core.exceptions import AppException, ErrorDetail

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_error_detail().model_dump()
        )
    
    @app.exception_handler(ValidationError)
    async def handle_validation_error(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorDetail(
                code="VALIDATION_ERROR",
                message="입력 데이터가 유효하지 않습니다",
                details={"errors": exc.errors()}
            ).model_dump()
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_error(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=500,
            content=ErrorDetail(
                code="DATABASE_ERROR",
                message="데이터베이스 오류가 발생했습니다",
                details={"error": str(exc)}
            ).model_dump()
        )
    
    @app.exception_handler(Exception)
    async def handle_general_exception(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=ErrorDetail(
                code="INTERNAL_ERROR",
                message="내부 서버 오류가 발생했습니다",
                details={"error": str(exc)}
            ).model_dump()
        )