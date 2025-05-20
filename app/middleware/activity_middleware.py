from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.activity_service import ActivityService
from app.models.activity import ActivityType, ActivityCategory
from app.models.memory import MemoryType
from typing import Callable, Dict, Any
import json

class ActivityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        activity_service: ActivityService,
        excluded_paths: set = None
    ):
        super().__init__(app)
        self.activity_service = activity_service
        self.excluded_paths = excluded_paths or {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        }

        # Map HTTP methods to activity types
        self.method_to_type: Dict[str, ActivityType] = {
            "GET": ActivityType.READ,
            "POST": ActivityType.CREATE,
            "PUT": ActivityType.UPDATE,
            "PATCH": ActivityType.UPDATE,
            "DELETE": ActivityType.DELETE
        }

        # Map paths to activity categories
        self.path_to_category: Dict[str, ActivityCategory] = {
            "/api/v1/auth": ActivityCategory.AUTHENTICATION,
            "/api/v1/memory": ActivityCategory.MEMORY,
            "/api/v1/files": ActivityCategory.FILE,
            "/api/v1/users": ActivityCategory.USER,
            "/api/v1/system": ActivityCategory.SYSTEM
        }

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Get user from request state
        user = getattr(request.state, "user", None)
        if not user:
            return await call_next(request)

        # Get activity type from HTTP method
        activity_type = self.method_to_type.get(request.method, ActivityType.SYSTEM)

        # Get activity category from path
        activity_category = ActivityCategory.SYSTEM
        for path_prefix, category in self.path_to_category.items():
            if request.url.path.startswith(path_prefix):
                activity_category = category
                break

        # Get request body if available
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except:
                pass

        # Create activity description
        description = f"{request.method} {request.url.path}"
        if body:
            description += f" with body: {json.dumps(body)}"

        # Log activity
        await self.activity_service.log_activity(
            activity_type=activity_type,
            category=activity_category,
            action=f"{request.method} {request.url.path}",
            description=description,
            user_id=user.id,
            business_id=user.business_id,
            metadata={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "body": body
            }
        )

        # Process request
        response = await call_next(request)

        return response 