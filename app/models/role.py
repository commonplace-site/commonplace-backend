from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, Table, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import BASE
from uuid import uuid4

# Association table for role permissions
role_permissions = Table(
    'role_permissions',
    BASE.metadata,
    Column('role_id', String(36), ForeignKey('roles.id')),
    Column('permission_id', String(36), ForeignKey('permissions.id'))
)

class Role(BASE):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    level = Column(Integer, nullable=False)  # Higher number means more privileges
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("UserRole", back_populates="role")

class Permission(BASE):
    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    resource = Column(String(50), nullable=False)  # e.g., "module", "profile", "log"
    action = Column(String(50), nullable=False)    # e.g., "create", "read", "update", "delete"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class UserRole(BASE):
    __tablename__ = "user_roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    role = relationship("Role", back_populates="users")

