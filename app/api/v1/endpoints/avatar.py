from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.avatar import avatar_service
from app.core.utils import get_current_user
from app.models.users import User

router = APIRouter(tags=["Avatar Generation"])

class AvatarRequest(BaseModel):
    text: str
    voice_id: str
    style: Optional[str] = "natural"
    emotion: Optional[str] = "neutral"
    background: Optional[str] = None

class AvatarResponse(BaseModel):
    video_url: str
    duration: float
    metadata: dict

@router.post("/avatar/generate", response_model=AvatarResponse)
async def generate_avatar(
    request: AvatarRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate an avatar video with synchronized speech
    """
    try:
        result = await avatar_service.generate_avatar(
            text=request.text,
            voice_id=request.voice_id,
            style=request.style,
            emotion=request.emotion,
            background=request.background
        )
        
        return AvatarResponse(
            video_url=result["video_url"],
            duration=result["duration"],
            metadata=result["metadata"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/avatar/list")
async def list_avatars(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available avatars
    """
    try:
        avatars = await avatar_service.get_available_avatars()
        return avatars
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

















































































































