from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging

from .api._router import router as api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 모든 테이블을 생성합니다.
    # 필요시, 별도의 쿼리로 관리해야 할 수 있습니다.
    # 데이터베이스는 사전에 생성해야 합니다.
    yield
    logger.warning("Shutting down the application")


app = FastAPI(
    title="BeyondX Local Trucking Platform",
    description="BeyondX Local Trucking Platform API Server",
    version="0.1.0",
    lifespan=lifespan,
)

# API 라우터 등록
app.include_router(api_router, prefix="/api")
