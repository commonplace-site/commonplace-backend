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

class ModuleCreate(BaseModel):
    name: str
    status: str = "active"
    active_user: int = 0

class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    active_user: Optional[int] = None

class LessonResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content_url: Optional[str] = None

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_url: Optional[str] = None 