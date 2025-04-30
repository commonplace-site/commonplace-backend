# from typing import Dict
# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# from app.core.utils import create_access_token, get_current_user, hash_password, verify_password
# from app.db.dependencies import get_db
# from app.models.users import User
# from app.schemas.user import Token, UserCreate
# from sqlalchemy.orm import Session
# router = APIRouter(
#     # prefix="/auth",
#     tags=["auth"]
# )

# session_cache: Dict[str, Dict] = {}

# @router.post("/token", response_model=Token)
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == form_data.username).first()
#     if not user or not (user.hashed_password == form_data.password + "notreallyhashed"):
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.get("/me")
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user



# # Signup route
# @router.post("/signup")
# def signup(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.username == user.username).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already exists")

#     new_user = User(
#         username=user.username,
#         password=hash_password(user.password),
#         role=user.role
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return {"msg": "User created", "role": new_user.role}

# # Login route
# @router.post("/login")
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": user.username, "role": user.role})
#     return {"access_token": token, "token_type": "bearer"}



from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.utils import create_access_token, create_reset_token, get_current_user, hash_password, verify_password, verify_reset_token
from app.db.dependencies import get_db
from app.models.users import User
from app.schemas.user import ForgotPasswordRequest, LoginSchema, ResetPasswordRequest, Token, UserCreate

router = APIRouter(tags=["auth"])

session_cache: Dict[str, Dict] = {}

# Signup route
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        role_id=3
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created", "role": new_user.role.name}

# Login route
# @router.post("/login", response_model=Token)
# def login(form_data: LoginSchema = Depends(), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == form_data.email).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": user.email, "role": user.role})
#     return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email, "role": user.role})  
    return {"access_token": token, "token_type": "bearer"}

# forgot_password route
# @router.post("/forgot-password")
# def forgot_password(email:str,db: Session= Depends(get_db)):
#     user=db.query(User).filter(User.email ==email).first()
#     if not user:
#         raise HTTPException(status_code=404,detail="user Not found")
#     reset_token=create_reset_token(user.email)
#     reset_link=f"http://localhost:8000/reset-password?token={reset_token}"
#     return{"msg":"Password reset link sent to your email"}


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
    
    


# Current user route
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
