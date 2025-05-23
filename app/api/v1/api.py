from fastapi import APIRouter
from app.api.v1.endpoints import (
    users, memory, role, ticket, auth, shadowbank, alam, developer, room127, mcp, chatbot
)

api_router = APIRouter()

# Core endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ticket.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])

# Additional endpoints
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(shadowbank.router, prefix="/shadowbank", tags=["shadowbank"])
api_router.include_router(alam.router, prefix="/alam", tags=["alam"])
api_router.include_router(developer.router, prefix="/developer", tags=["developer"])
api_router.include_router(room127.router, prefix="/room127", tags=["room127"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"]) 