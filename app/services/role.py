from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.role import Role, Permission, UserRole
from app.schemas.role import RoleCreate, RoleUpdate, UserRoleUpdate
from app.core.rbac import ROLE_PERMISSIONS, DEFAULT_PERMISSIONS

class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role"""
        role = Role(
            id=role_data.id,
            description=role_data.description
        )
        
        # Add permissions
        for perm_id in role_data.permissions:
            permission = self.db.query(Permission).filter(Permission.id == perm_id).first()
            if permission:
                role.permissions.append(permission)
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role_id: str, role_data: RoleUpdate) -> Optional[Role]:
        """Update a role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None

        if role_data.description is not None:
            role.description = role_data.description

        if role_data.permissions is not None:
            role.permissions = []
            for perm_id in role_data.permissions:
                permission = self.db.query(Permission).filter(Permission.id == perm_id).first()
                if permission:
                    role.permissions.append(permission)

        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False

        self.db.delete(role)
        self.db.commit()
        return True

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get a role by ID"""
        return self.db.query(Role).filter(Role.id == role_id).first()

    def list_roles(self) -> List[Role]:
        """List all roles"""
        return self.db.query(Role).all()

    def update_user_roles(self, user_id: str, role_data: UserRoleUpdate) -> bool:
        """Update user roles"""
        # Remove existing roles
        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        
        # Add new roles
        for role_id in role_data.roles:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
        
        self.db.commit()
        return True

    def get_user_roles(self, user_id: str) -> List[str]:
        """Get all roles for a user"""
        user_roles = self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
        return [ur.role_id for ur in user_roles]

    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user"""
        user_roles = self.get_user_roles(user_id)
        permissions = set()
        
        for role_id in user_roles:
            if role_id in ROLE_PERMISSIONS:
                permissions.update(ROLE_PERMISSIONS[role_id])
        
        return list(permissions)

    def create_permission(self, permission_id: str, description: str) -> Permission:
        """Create a new permission"""
        permission = Permission(
            id=permission_id,
            description=description
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def list_permissions(self) -> List[Permission]:
        """List all permissions"""
        return self.db.query(Permission).all()

    def initialize_permissions(self) -> None:
        """Initialize default permissions"""
        for perm_id, description in DEFAULT_PERMISSIONS.items():
            permission = self.db.query(Permission).filter(Permission.id == perm_id).first()
            if not permission:
                self.create_permission(perm_id, description) 