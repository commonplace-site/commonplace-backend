from typing import Dict, List, Optional
from app.models.role import Role, Permission, UserRole
from app.db.database import BASE
from sqlalchemy.orm import Session

# Define default permissions
DEFAULT_PERMISSIONS = {
    # Ticket permissions
    "ticket:create": "Create new tickets",
    "ticket:read": "View tickets and their details",
    "ticket:update": "Update ticket information",
    "ticket:delete": "Delete tickets",
    "ticket:comment": "Add and manage comments on tickets",
    "ticket:assign": "Assign tickets to users",
    "ticket:close": "Close and resolve tickets",
    
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