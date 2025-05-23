from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from .core.exception_handlers import setup_exception_handlers
from .api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    logger.warning("Shutting down the application")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response


app = FastAPI(
    title="BeyondX Local Trucking Platform",
    description="BeyondX Local Trucking Platform API Server",
    version="0.1.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SecurityHeadersMiddleware,
)


# API 라우터 등록
app.include_router(api_router, prefix="/api")
setup_exception_handlers(app)
