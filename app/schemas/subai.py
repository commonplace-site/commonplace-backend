from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class SubAIRequest(BaseModel):
    user_id: str
    prompt: str
    model: str
    response: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SubAIResponse(BaseModel):
    id: str
    prompt: str
    model: str
    response: Dict[str, Any]
    created_at: datetime

class SubAILogResponse(SubAIResponse):
    metadata: Dict[str, Any]
    updated_at: Optional[datetime] = None 