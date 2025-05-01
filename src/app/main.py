from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    # 모든 테이블을 생성합니다.
    # 필요시, 별도의 쿼리로 관리해야 할 수 있습니다.
    # 데이터베이스는 사전에 생성해야 합니다.
    yield
    logger.warning("Shutting down the application")
  
app = FastAPI(lifespan=lifespan)
