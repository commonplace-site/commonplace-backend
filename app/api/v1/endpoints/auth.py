from typing import Dict, Set
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.utils import create_access_token, create_reset_token, get_current_token, get_current_user, hash_password, role_required, verify_password, verify_reset_token
from app.db.dependencies import get_db
from app.models.users import User
from app.schemas.user import ForgotPasswordRequest, LoginSchema, ResetPasswordRequest, Token, UserCreate

router = APIRouter(tags=["auth"])

session_cache: Dict[str, Dict] = {}
token_blacklist: Set[str] = set()
# Signup route
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        first_Name=user.first_Name,
        last_Name=user.last_Name,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default user role
    from app.models.role import UserRole
    user_role = UserRole(
        user_id=new_user.id,
        role_id=3,  
        is_active=True
    )
    db.add(user_role)
    db.commit()
    
    return {"msg": "User created", "role": user_role.role.name, "id": new_user.id}

# Login route
@router.post("/login", response_model=Token)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get the active role for the user
    active_role = next((ur.role for ur in user.user_roles if ur.is_active), None)
    if not active_role:
        raise HTTPException(status_code=400, detail="No active role assigned to user")
    
    token = create_access_token({
        "sub": user.email,
        "role": active_role.name 
    })
    return {"access_token": token, "token_type": "bearer"}

# forgot_password route
@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = payload.email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(user.email)
    reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
    # Here you would send the reset link to the user's email
    return {"msg": "Password reset link sent to your email","Token":reset_token}

# Reset-password
@router.post("/reset-password")
def reset_password(data:ResetPasswordRequest, db:Session = Depends(get_db)):
    email = verify_reset_token(data.token)
    if not email: 
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user=db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password=hash_password(data.new_password)
    db.commit()
    return{"msg":"Password Reset successful"}
    
    
@router.post("/logout")
def logout(token: str = Depends(get_current_token)):
    token_blacklist.add(token)
    return {"detail": "Successfully logged out"}    


# Current user route
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/admin")
def admin_route(user=Depends(role_required("Admin"))):
    return{"msg":f"Welcome {user.first_Name}"}