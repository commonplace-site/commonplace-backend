from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ModuleResponse(BaseModel):
    id: int
    name: str
    status: str
    active_user: int
    last_updated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LessonResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 