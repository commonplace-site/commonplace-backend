from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID

class BusinessBase(BaseModel):
    name: str
    license_key: str
    established_date: datetime
    renewal_due_date: datetime

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    license_key: Optional[str] = None
    renewal_due_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class BusinessUserBase(BaseModel):
    user_id: UUID
    role: str
    is_active: bool = True

class BusinessUserCreate(BusinessUserBase):
    business_id: UUID

class BusinessUserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

class BusinessResponse(BusinessBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BusinessUserResponse(BusinessUserBase):
    business_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 