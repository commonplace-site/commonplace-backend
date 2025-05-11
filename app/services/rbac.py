from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role import Role, Permission, UserRole
from app.schemas.role import RoleCreate, RoleUpdate, UserRoleCreate, UserRoleUpdate

class RBACService:
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role_data: RoleCreate) -> Role:
        role = Role(
            name=role_data.name,
            description=role_data.description,
            level=role_data.level,
            is_active=role_data.is_active
        )
        
        if role_data.permission_ids:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            role.permissions = permissions
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role(self, role_id: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_role_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def update_role(self, role_id: str, role_data: RoleUpdate) -> Optional[Role]:
        role = self.get_role(role_id)
        if not role:
            return None

        for field, value in role_data.dict(exclude_unset=True).items():
            if field == "permission_ids":
                if value is not None:
                    permissions = self.db.query(Permission).filter(
                        Permission.id.in_(value)
                    ).all()
                    role.permissions = permissions
            else:
                setattr(role, field, value)

        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: str) -> bool:
        role = self.get_role(role_id)
        if not role:
            return False
        
        self.db.delete(role)
        self.db.commit()
        return True

    def create_permission(self, name: str, resource: str, action: str, description: Optional[str] = None) -> Permission:
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_permission(self, permission_id: str) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.id == permission_id).first()

    def assign_role_to_user(self, user_role_data: UserRoleCreate) -> UserRole:
        user_role = UserRole(**user_role_data.dict())
        self.db.add(user_role)
        self.db.commit()
        self.db.refresh(user_role)
        return user_role

    def get_user_roles(self, user_id: str) -> List[UserRole]:
        return self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.is_active == True
        ).all()

    def update_user_role(self, user_role_id: str, user_role_data: UserRoleUpdate) -> Optional[UserRole]:
        user_role = self.db.query(UserRole).filter(UserRole.id == user_role_id).first()
        if not user_role:
            return None

        for field, value in user_role_data.dict(exclude_unset=True).items():
            setattr(user_role, field, value)

        self.db.commit()
        self.db.refresh(user_role)
        return user_role

    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        user_roles = self.get_user_roles(user_id)
        for user_role in user_roles:
            for permission in user_role.role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        return False

    def get_user_permissions(self, user_id: str) -> List[Permission]:
        user_roles = self.get_user_roles(user_id)
        permissions = set()
        for user_role in user_roles:
            permissions.update(user_role.role.permissions)
        return list(permissions)