from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.core.rbac import require_permission, require_minimum_role_level
from app.models.memory import UserProfile, ModuleState, CodexLog, Room127Log, DeveloperLog, AuditLog, UserRole
from app.schemas.memory import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    ModuleStateCreate, ModuleStateUpdate, ModuleStateResponse,
    CodexLogCreate, CodexLogResponse,
    Room127LogCreate, Room127LogResponse,
    DeveloperLogCreate, DeveloperLogResponse,
    AuditLogResponse
)

router = APIRouter()

# Helper function for RBAC
def check_permission(user_role: UserRole, required_role: UserRole) -> bool:
    role_hierarchy = {
        UserRole.ADMIN: 4,
        UserRole.TEACHER: 3,
        UserRole.MODERATOR: 2,
        UserRole.DEVELOPER: 2,
        UserRole.STUDENT: 1
    }
    return role_hierarchy[user_role] >= role_hierarchy[required_role]

# Helper function for audit logging
def create_audit_log(db: Session, module_state_id: str, action: str, actor_id: str, changes: dict):
    audit_log = AuditLog(
        module_state_id=module_state_id,
        action=action,
        actor_id=actor_id,
        changes=changes
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

# User Profile endpoints
@router.post("/profiles", response_model=UserProfileResponse)
def create_user_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("profile", "create"))
):
    db_profile = UserProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/profiles/{user_id}", response_model=UserProfileResponse)
def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("profile", "read"))
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    return profile

@router.put("/profiles/{user_id}", response_model=UserProfileResponse)
def update_user_profile(
    user_id: str,
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("profile", "update"))
):
    db_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    for field, value in profile_update.dict(exclude_unset=True).items():
        setattr(db_profile, field, value)
    
    db_profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_profile)
    return db_profile

# Module State endpoints
@router.post("/modules/{module_id}/users/{user_id}", response_model=ModuleStateResponse)
def create_module_state(
    module_id: str,
    user_id: str,
    state: ModuleStateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("module", "create"))
):
    db_state = ModuleState(**state.dict())
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    
    create_audit_log(
        db=db,
        module_state_id=str(db_state.id),
        action="create",
        actor_id=current_user["id"],
        changes={"state": state.dict()}
    )
    
    return db_state

@router.get("/modules/{module_id}/users/{user_id}", response_model=ModuleStateResponse)
def get_module_state(
    module_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("module", "read"))
):
    state = db.query(ModuleState).filter(
        ModuleState.module_id == module_id,
        ModuleState.user_id == user_id
    ).first()
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module state not found"
        )
    
    return state

@router.put("/modules/{module_id}/users/{user_id}", response_model=ModuleStateResponse)
def update_module_state(
    module_id: str,
    user_id: str,
    state_update: ModuleStateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("module", "update"))
):
    db_state = db.query(ModuleState).filter(
        ModuleState.module_id == module_id,
        ModuleState.user_id == user_id
    ).first()
    
    if not db_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module state not found"
        )
    
    old_state = db_state.dict()
    for field, value in state_update.dict(exclude_unset=True).items():
        setattr(db_state, field, value)
    
    db_state.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_state)
    
    create_audit_log(
        db=db,
        module_state_id=str(db_state.id),
        action="update",
        actor_id=current_user["id"],
        changes={
            "old_state": old_state,
            "new_state": state_update.dict(exclude_unset=True)
        }
    )
    
    return db_state

# Codex Log endpoints
@router.post("/codex/logs", response_model=CodexLogResponse)
def create_codex_log(
    log: CodexLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("codex", "create"))
):
    db_log = CodexLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/codex/logs/{user_id}", response_model=List[CodexLogResponse])
def get_codex_logs(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("codex", "read"))
):
    logs = db.query(CodexLog).filter(CodexLog.user_id == user_id).all()
    return logs

# Room 127 Log endpoints
@router.post("/room127/logs", response_model=Room127LogResponse)
def create_room127_log(
    log: Room127LogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("room127", "create"))
):
    db_log = Room127Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/room127/logs/{user_id}", response_model=List[Room127LogResponse])
def get_room127_logs(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("room127", "read"))
):
    logs = db.query(Room127Log).filter(Room127Log.user_id == user_id).all()
    return logs

# Developer Log endpoints
@router.post("/developer/logs", response_model=DeveloperLogResponse)
def create_developer_log(
    log: DeveloperLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("developer", "create"))
):
    db_log = DeveloperLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/developer/logs/{user_id}", response_model=List[DeveloperLogResponse])
def get_developer_logs(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("developer", "read"))
):
    logs = db.query(DeveloperLog).filter(DeveloperLog.user_id == user_id).all()
    return logs

# Audit Log endpoints
@router.get("/audit-logs/{module_state_id}", response_model=List[AuditLogResponse])
def get_audit_logs(
    module_state_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("audit", "read"))
):
    logs = db.query(AuditLog).filter(AuditLog.module_state_id == module_state_id).all()
    return logs 