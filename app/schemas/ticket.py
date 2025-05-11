from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.ticket import TicketStatus, TicketPriority, TicketType

class TicketBase(BaseModel):
    title: str
    description: str
    type: TicketType
    priority: TicketPriority = TicketPriority.MEDIUM
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    due_date: Optional[datetime] = None

class TicketCreate(TicketBase):
    assigned_to: Optional[str] = None

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    type: Optional[TicketType] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    due_date: Optional[datetime] = None

class TicketCommentBase(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TicketCommentCreate(TicketCommentBase):
    pass

class TicketCommentUpdate(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TicketCommentResponse(TicketCommentBase):
    id: str
    ticket_id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TicketHistoryResponse(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    action: str
    changes: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class TicketResponse(TicketBase):
    id: str
    status: TicketStatus
    created_by: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    comments: List[TicketCommentResponse] = []
    history: List[TicketHistoryResponse] = []

    class Config:
        from_attributes = True

class TicketFilter(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    type: Optional[TicketType] = None
    assigned_to: Optional[str] = None
    created_by: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    due_before: Optional[datetime] = None 