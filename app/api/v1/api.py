from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, memory, ticket, role
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(ticket.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"]) 