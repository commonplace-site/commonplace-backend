from typing import Dict, List, Optional
from app.core.utils import get_current_user
from app.db.dependencies import get_db
from app.models.role import Role, Permission, UserRole
from app.db.database import BASE
from sqlalchemy.orm import Session
from app.models.business import business_users
from fastapi import Depends, HTTPException, status
from app.services.rbac import RBACService
# from app.db.database import get_db

# Define default permissions
DEFAULT_PERMISSIONS = {
    # Business permissions
    "business:create": "Create new businesses",
    "business:read": "View business information",
    "business:update": "Update business information",
    "business:delete": "Delete businesses",
    "business:manage_users": "Manage business users",
    "business:manage_modules": "Manage business modules",
    "business:manage_lessons": "Manage business lessons",
    
    # Business role permissions
    "business_admin:manage": "Manage business administration",
    "business_teacher:manage": "Manage business teaching",
    "business_student:manage": "Manage business students",
    "business_moderator:manage": "Manage business content moderation",
    
    # Existing permissions
    "user:create": "Create new users",
    "user:read": "View user information",
    "user:update": "Update user information",
    "user:delete": "Delete users",
    "role:manage": "Manage roles and permissions",
    "module:create": "Create new modules",
    "module:read": "View module information",
    "module:update": "Update module information",
    "module:delete": "Delete modules",
    "module:approve": "Approve module changes",
    "module:review": "Review module content",
}

# Define role-permission mappings
ROLE_PERMISSIONS = {
    "admin": [
        "ticket:create", "ticket:read", "ticket:update", "ticket:delete",
        "ticket:comment", "ticket:assign", "ticket:close",
        "user:create", "user:read", "user:update", "user:delete",
        "role:manage", "module:create", "module:read", "module:update",
        "module:delete", "module:approve", "module:review"
    ],
    "manager": [
        "ticket:create", "ticket:read", "ticket:update", "ticket:delete",
        "ticket:comment", "ticket:assign", "ticket:close",
        "user:read", "module:create", "module:read", "module:update",
        "module:review"
    ],
    "developer": [
        "ticket:create", "ticket:read", "ticket:update",
        "ticket:comment", "module:read"
    ],
    "teacher": [
        "ticket:create", "ticket:read", "ticket:update",
        "ticket:comment", "module:read", "module:review"
    ],
    "student": [
        "ticket:create", "ticket:read", "ticket:comment",
        "module:read"
    ]
}

# Define role hierarchy
ROLE_HIERARCHY = {
    "root_admin": 5,  # Can manage all businesses
    "business_admin": 4,  # Can manage single business
    "business_teacher": 3,
    "business_moderator": 2,
    "business_student": 1
}

def check_permission(user: Dict, permission: str) -> bool:
    """Check if a user has a specific permission"""
    if not user or "role" not in user:
        return False
    
    user_role = user["role"]
    if user_role not in ROLE_PERMISSIONS:
        return False
    
    return permission in ROLE_PERMISSIONS[user_role]

def get_user_permissions(user: Dict) -> List[str]:
    """Get all permissions for a user"""
    if not user or "role" not in user:
        return []
    
    user_role = user["role"]
    return ROLE_PERMISSIONS.get(user_role, [])

def initialize_rbac(db: Session) -> None:
    """Initialize RBAC system with default roles and permissions"""
    # Create permissions
    for perm_id, description in DEFAULT_PERMISSIONS.items():
        permission = db.query(Permission).filter(Permission.id == perm_id).first()
        if not permission:
            permission = Permission(id=perm_id, description=description)
            db.add(permission)
    
    # Create roles and assign permissions
    for role_id, permissions in ROLE_PERMISSIONS.items():
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            role = Role(id=role_id, description=f"{role_id.capitalize()} role")
            db.add(role)
        
        # Assign permissions to role
        for perm_id in permissions:
            permission = db.query(Permission).filter(Permission.id == perm_id).first()
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
    
    db.commit()

def assign_role_to_user(user_id: str, role_id: str, db: Session) -> bool:
    """Assign a role to a user"""
    if role_id not in ROLE_PERMISSIONS:
        return False
    
    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    db.commit()
    return True

def remove_role_from_user(user_id: str, role_id: str, db: Session) -> bool:
    """Remove a role from a user"""
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    
    if user_role:
        db.delete(user_role)
        db.commit()
        return True
    return False

def get_user_roles(user_id: str, db: Session) -> List[str]:
    """Get all roles for a user"""
    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    return [ur.role_id for ur in user_roles]

def require_permission(resource: str, action: str):
    """
    FastAPI dependency that checks if the current user has the required permission.
    Usage: Depends(require_permission("resource", "action"))
    """
    async def _require_permission(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
        rbac_service = RBACService(db)
        if not rbac_service.check_permission(current_user["id"], resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {resource}:{action}"
            )
        return current_user
    return _require_permission

def check_business_permission(user_id: str, business_id: str, required_permission: str, db: Session) -> bool:
    """Check if user has required permission for a specific business"""
    # Get user's business role
    business_user = db.query(business_users).filter(
        business_users.c.user_id == user_id,
        business_users.c.business_id == business_id,
        business_users.c.is_active == True
    ).first()
    
    if not business_user:
        return False
        
    # Check if user's role has the required permission
    role_permissions = get_role_permissions(business_user.role)
    return required_permission in role_permissions

def get_role_permissions(role: str) -> List[str]:
    """Get permissions for a specific role"""
    role_permissions = {
        "root_admin": list(DEFAULT_PERMISSIONS.keys()),
        "business_admin": [
            "business:read",
            "business:update",
            "business:manage_users",
            "business:manage_modules",
            "business:manage_lessons",
            "module:create",
            "module:read",
            "module:update",
            "module:delete",
            "user:read",
            "user:update"
        ],
        "business_teacher": [
            "business:read",
            "module:create",
            "module:read",
            "module:update",
            "user:read"
        ],
        "business_moderator": [
            "business:read",
            "module:read",
            "module:review"
        ],
        "business_student": [
            "business:read",
            "module:read"
        ]
    }
    return role_permissions.get(role, []) 