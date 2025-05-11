from sqlalchemy.orm import Session
from app.services.rbac import RBACService
from app.models.role import Role, Permission

def init_rbac(db: Session):
    rbac_service = RBACService(db)
    
    # Create permissions
    permissions = {
        # Profile permissions
        "profile_create": rbac_service.create_permission(
            "Create Profile",
            "profile",
            "create",
            "Create user profiles"
        ),
        "profile_read": rbac_service.create_permission(
            "Read Profile",
            "profile",
            "read",
            "Read user profiles"
        ),
        "profile_update": rbac_service.create_permission(
            "Update Profile",
            "profile",
            "update",
            "Update user profiles"
        ),
        
        # Module permissions
        "module_create": rbac_service.create_permission(
            "Create Module",
            "module",
            "create",
            "Create module states"
        ),
        "module_read": rbac_service.create_permission(
            "Read Module",
            "module",
            "read",
            "Read module states"
        ),
        "module_update": rbac_service.create_permission(
            "Update Module",
            "module",
            "update",
            "Update module states"
        ),
        
        # Codex permissions
        "codex_create": rbac_service.create_permission(
            "Create Codex Log",
            "codex",
            "create",
            "Create Codex logs"
        ),
        "codex_read": rbac_service.create_permission(
            "Read Codex Log",
            "codex",
            "read",
            "Read Codex logs"
        ),
        
        # Room 127 permissions
        "room127_create": rbac_service.create_permission(
            "Create Room 127 Log",
            "room127",
            "create",
            "Create Room 127 logs"
        ),
        "room127_read": rbac_service.create_permission(
            "Read Room 127 Log",
            "room127",
            "read",
            "Read Room 127 logs"
        ),
        
        # Developer permissions
        "developer_create": rbac_service.create_permission(
            "Create Developer Log",
            "developer",
            "create",
            "Create developer logs"
        ),
        "developer_read": rbac_service.create_permission(
            "Read Developer Log",
            "developer",
            "read",
            "Read developer logs"
        ),
        
        # Audit permissions
        "audit_read": rbac_service.create_permission(
            "Read Audit Log",
            "audit",
            "read",
            "Read audit logs"
        ),
    }
    
    # Create roles with permissions
    roles = {
        "admin": rbac_service.create_role({
            "name": "admin",
            "description": "Administrator with full access",
            "level": 4,
            "permission_ids": [p.id for p in permissions.values()]
        }),
        
        "teacher": rbac_service.create_role({
            "name": "teacher",
            "description": "Teacher with access to student data and module management",
            "level": 3,
            "permission_ids": [
                permissions["profile_read"].id,
                permissions["module_create"].id,
                permissions["module_read"].id,
                permissions["module_update"].id,
                permissions["codex_read"].id,
                permissions["room127_read"].id
            ]
        }),
        
        "student": rbac_service.create_role({
            "name": "student",
            "description": "Student with access to their own data",
            "level": 1,
            "permission_ids": [
                permissions["profile_read"].id,
                permissions["module_read"].id,
                permissions["codex_create"].id,
                permissions["room127_create"].id
            ]
        }),
        
        "developer": rbac_service.create_role({
            "name": "developer",
            "description": "Developer with access to development tools",
            "level": 2,
            "permission_ids": [
                permissions["developer_create"].id,
                permissions["developer_read"].id,
                permissions["module_read"].id
            ]
        }),
        
        "moderator": rbac_service.create_role({
            "name": "moderator",
            "description": "Moderator with access to content moderation",
            "level": 2,
            "permission_ids": [
                permissions["profile_read"].id,
                permissions["module_read"].id,
                permissions["codex_read"].id,
                permissions["room127_read"].id
            ]
        })
    }
    
    return roles 