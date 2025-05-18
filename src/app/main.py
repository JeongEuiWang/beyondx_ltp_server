from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from .core.exception_handlers import setup_exception_handlers
from .api import router as api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
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
setup_exception_handlers(app)  # 여기에 추가
