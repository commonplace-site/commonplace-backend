from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.utils import get_current_user, verify_token
from app.db.dependencies import get_db
from app.models.subai_log import SubAILog
from app.models.users import User
from app.schemas.subai import SubAIRequest, SubAIResponse, SubAILogResponse

router = APIRouter(tags=["Sub-AI"])

@router.post("/subai/generate", response_model=SubAIResponse)
async def generate_subai_response(
    request: SubAIRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Generate a response using the specified sub-AI model
    """
    verify_token(authorization)
    
    try:
        # Create subai log entry
        subai_log = SubAILog(
            user_id=request.user_id,
            prompt=request.prompt,
            model=request.model,
            response=request.response,
            metadata=request.metadata
        )
        
        db.add(subai_log)
        db.commit()
        db.refresh(subai_log)
        
        return SubAIResponse(
            id=subai_log.id,
            prompt=subai_log.prompt,
            model=subai_log.model,
            response=subai_log.response,
            created_at=subai_log.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subai/history", response_model=List[SubAILogResponse])
async def get_subai_history(
    model: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Sub-AI interaction history for the current user
    """
    query = db.query(SubAILog).filter(SubAILog.user_id == str(current_user.id))
    
    if model:
        query = query.filter(SubAILog.model == model)
        
    logs = query.order_by(SubAILog.created_at.desc()).all()
    return logs 