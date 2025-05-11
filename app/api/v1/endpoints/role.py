from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rbac import check_permission
from app.services.role import RoleService
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse,
    PermissionResponse, UserRoleUpdate, UserRoleResponse
)

router = APIRouter()

@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new role (Admin only)"""
    check_permission(current_user, "role:manage")
    role_service = RoleService(db)
    role = role_service.create_role(role_data)
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a role (Admin only)"""
    check_permission(current_user, "role:manage")
    role_service = RoleService(db)
    role = role_service.update_role(role_id, role_data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a role (Admin only)"""
    check_permission(current_user, "role:manage")
    role_service = RoleService(db)
    if not role_service.delete_role(role_id):
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all roles (Admin only)"""
    check_permission(current_user, "role:manage")
    role_service = RoleService(db)
    return role_service.list_roles()

@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all permissions (Admin only)"""
    check_permission(current_user, "role:manage")
    role_service = RoleService(db)
    return role_service.list_permissions()

@router.put("/users/{user_id}/roles", response_model=UserRoleResponse)
async def update_user_roles(
    user_id: str,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user roles (Admin only)"""
    check_permission(current_user, "role:manage")
    role_service = RoleService(db)
    
    if not role_service.update_user_roles(user_id, role_data):
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserRoleResponse(
        user_id=user_id,
        roles=role_service.get_user_roles(user_id),
        permissions=role_service.get_user_permissions(user_id)
    )

@router.get("/users/{user_id}/roles", response_model=UserRoleResponse)
async def get_user_roles(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user roles and permissions (Admin only)"""
    check_permission(current_user, "role:manage")
    role_service = RoleService(db)
    
    roles = role_service.get_user_roles(user_id)
    if not roles:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserRoleResponse(
        user_id=user_id,
        roles=roles,
        permissions=role_service.get_user_permissions(user_id)
    ) 