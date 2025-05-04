from fastapi import APIRouter

from .auth import router as auth_router
from .user import router as user_router
from .rate import router as rate_router
from .cargo import router as cargo_router
router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(rate_router)
router.include_router(cargo_router)