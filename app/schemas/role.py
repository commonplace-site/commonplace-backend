from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PermissionBase(BaseModel):
    id: str
    description: str

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    id: str
    description: str
    permissions: List[str] = Field(default_factory=list)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleResponse(RoleBase):
    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    roles: List[str]

class UserRoleResponse(BaseModel):
    user_id: str
    roles: List[str]
    permissions: List[str]

    class Config:
        from_attributes = True 