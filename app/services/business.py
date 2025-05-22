from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.business import Business, business_users
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessUserCreate, BusinessUserUpdate
from uuid import UUID
from fastapi import HTTPException, status

class BusinessService:
    def __init__(self, db: Session):
        self.db = db

    def create_business(self, business_data: BusinessCreate, creator_id: UUID) -> Business:
        """Create a new business (root admin only)"""
        # Check if creator is root admin
        creator_role = self.db.query(business_users).filter(
            business_users.c.user_id == creator_id,
            business_users.c.role == "root_admin"
        ).first()
        
        if not creator_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only root admin can create businesses"
            )
            
        business = Business(**business_data.dict())
        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)
        return business

    def get_business(self, business_id: UUID, user_id: UUID) -> Optional[Business]:
        """Get business by ID with access control"""
        # Check if user has access to this business
        business_user = self.db.query(business_users).filter(
            business_users.c.user_id == user_id,
            business_users.c.business_id == business_id,
            business_users.c.is_active == True
        ).first()
        
        if not business_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this business"
            )
            
        return self.db.query(Business).filter(Business.id == business_id).first()

    def update_business(self, business_id: UUID, business_data: BusinessUpdate, user_id: UUID) -> Optional[Business]:
        """Update business information with access control"""
        # Check if user is business admin or root admin
        business_user = self.db.query(business_users).filter(
            business_users.c.user_id == user_id,
            business_users.c.business_id == business_id,
            business_users.c.role.in_(["business_admin", "root_admin"]),
            business_users.c.is_active == True
        ).first()
        
        if not business_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only business admin or root admin can update business"
            )
            
        business = self.get_business(business_id, user_id)
        if not business:
            return None

        for key, value in business_data.dict(exclude_unset=True).items():
            setattr(business, key, value)

        self.db.commit()
        self.db.refresh(business)
        return business

    def delete_business(self, business_id: UUID, user_id: UUID) -> bool:
        """Delete a business (root admin only)"""
        # Check if user is root admin
        is_root_admin = self.db.query(business_users).filter(
            business_users.c.user_id == user_id,
            business_users.c.role == "root_admin"
        ).first()
        
        if not is_root_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only root admin can delete businesses"
            )
            
        business = self.get_business(business_id, user_id)
        if not business:
            return False

        self.db.delete(business)
        self.db.commit()
        return True

    def add_user_to_business(self, user_data: BusinessUserCreate, admin_id: UUID) -> bool:
        """Add a user to a business with access control"""
        # Check if admin has permission to add users
        admin_role = self.db.query(business_users).filter(
            business_users.c.user_id == admin_id,
            business_users.c.business_id == user_data.business_id,
            business_users.c.role.in_(["business_admin", "root_admin"]),
            business_users.c.is_active == True
        ).first()
        
        if not admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only business admin or root admin can add users"
            )
            
        stmt = business_users.insert().values(**user_data.dict())
        self.db.execute(stmt)
        self.db.commit()
        return True

    def update_user_role(self, business_id: UUID, user_id: UUID, user_data: BusinessUserUpdate, admin_id: UUID) -> bool:
        """Update a user's role in a business with access control"""
        # Check if admin has permission to update roles
        admin_role = self.db.query(business_users).filter(
            business_users.c.user_id == admin_id,
            business_users.c.business_id == business_id,
            business_users.c.role.in_(["business_admin", "root_admin"]),
            business_users.c.is_active == True
        ).first()
        
        if not admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only business admin or root admin can update roles"
            )
            
        stmt = business_users.update().where(
            business_users.c.business_id == business_id,
            business_users.c.user_id == user_id
        ).values(**user_data.dict(exclude_unset=True))
        
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def remove_user_from_business(self, business_id: UUID, user_id: UUID, admin_id: UUID) -> bool:
        """Remove a user from a business with access control"""
        # Check if admin has permission to remove users
        admin_role = self.db.query(business_users).filter(
            business_users.c.user_id == admin_id,
            business_users.c.business_id == business_id,
            business_users.c.role.in_(["business_admin", "root_admin"]),
            business_users.c.is_active == True
        ).first()
        
        if not admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only business admin or root admin can remove users"
            )
            
        stmt = business_users.delete().where(
            business_users.c.business_id == business_id,
            business_users.c.user_id == user_id
        )
        
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def get_business_users(self, business_id: UUID, user_id: UUID) -> List[dict]:
        """Get all users in a business with access control"""
        # Check if user has access to this business
        business_user = self.db.query(business_users).filter(
            business_users.c.user_id == user_id,
            business_users.c.business_id == business_id,
            business_users.c.is_active == True
        ).first()
        
        if not business_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this business"
            )
            
        return self.db.query(business_users).filter(
            business_users.c.business_id == business_id
        ).all()

    def get_user_businesses(self, user_id: UUID) -> List[Business]:
        """Get all businesses a user belongs to"""
        return self.db.query(Business).join(
            business_users,
            Business.id == business_users.c.business_id
        ).filter(
            business_users.c.user_id == user_id,
            business_users.c.is_active == True
        ).all() 