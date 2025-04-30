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

from app.core.utils import create_access_token, get_current_user, hash_password, verify_password
from app.db.dependencies import get_db
from app.models.users import User
from app.schemas.user import LoginSchema, Token, UserCreate

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


# Current user route
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
