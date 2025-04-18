from fastapi import APIRouter
from .endpoints.users import router as user_router
from .endpoints.auth import router as auth_router


router = APIRouter()


# api/routes/__init__.py


router.include_router(user_router)
router.include_router(auth_router)
