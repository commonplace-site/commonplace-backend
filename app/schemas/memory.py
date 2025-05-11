from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ModuleState(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DRAFT = "draft"
    REVIEW = "review"

class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    DEVELOPER = "developer"
    MODERATOR = "moderator"

class UserProfileBase(BaseModel):
    user_id: str
    role: UserRole = UserRole.STUDENT
    preferences: Dict[str, Any] = Field(default_factory=dict)
    learning_stats: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(BaseModel):
    role: Optional[UserRole] = None
    preferences: Optional[Dict[str, Any]] = None
    learning_stats: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class UserProfileResponse(UserProfileBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_active: datetime
    is_active: bool

    class Config:
        from_attributes = True

class ModuleStateBase(BaseModel):
    user_id: str
    module_id: str
    state: ModuleState = ModuleState.ACTIVE
    progress: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ModuleStateCreate(ModuleStateBase):
    pass

class ModuleStateUpdate(BaseModel):
    state: Optional[ModuleState] = None
    progress: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ModuleStateResponse(ModuleStateBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_accessed: datetime

    class Config:
        from_attributes = True

class CodexLogBase(BaseModel):
    user_id: str
    content: str
    context: str
    analysis: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CodexLogCreate(CodexLogBase):
    pass

class CodexLogResponse(CodexLogBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Room127LogBase(BaseModel):
    user_id: str
    content: str
    context: str
    feedback: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Room127LogCreate(Room127LogBase):
    pass

class Room127LogResponse(Room127LogBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class DeveloperLogBase(BaseModel):
    user_id: str
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DeveloperLogCreate(DeveloperLogBase):
    pass

class DeveloperLogResponse(DeveloperLogBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogBase(BaseModel):
    module_state_id: str
    action: str
    actor_id: str
    changes: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True 