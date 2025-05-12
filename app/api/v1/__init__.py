from fastapi import APIRouter
from .endpoints.users import router as user_router
from .endpoints.auth import router as auth_router
from .endpoints.shadowbank import router as shadow_bank_router
from .endpoints.alam import router as alam_router
from .endpoints.developer import router as developer_route
from .endpoints.room127 import router as room127_router
from .endpoints.mcp import router as mcp_router
# from app.api.v1.endpoints import (
#     auth, users, memory, ticket, role
# )

# api_router = APIRouter()

# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
# api_router.include_router(ticket.router, prefix="/tickets", tags=["tickets"])
# api_router.include_router(role.router, prefix="/roles", tags=["roles"]) 


router = APIRouter()



router.include_router(user_router)
router.include_router(auth_router)
router.include_router(shadow_bank_router)
router.include_router(alam_router)
router.include_router(developer_route)
router.include_router(room127_router)
router.include_router(mcp_router)
