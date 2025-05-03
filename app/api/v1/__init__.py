from fastapi import APIRouter
from .endpoints.users import router as user_router
from .endpoints.auth import router as auth_router
from .endpoints.shadowbank import router as shadow_bank_router
from .endpoints.alam import router as alam_router



router = APIRouter()


# api/routes/__init__.py


router.include_router(user_router)
router.include_router(auth_router)
router.include_router(shadow_bank_router)
router.include_router(alam_router)
