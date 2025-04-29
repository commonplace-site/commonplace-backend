from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.utils import create_access_token, get_current_user
from app.db.dependencies import get_db
from app.models.users import User
from app.schemas.user import Token, UserCreate
from sqlalchemy.orm import Session
router = APIRouter(
    # prefix="/auth",
    tags=["auth"]
)

session_cache: Dict[str, Dict] = {}

@router.get("/login")
def login():
    return {"message":"message user login will be here"}


@router.post("/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = user_data.password + "notreallyhashed"  # Replace with real hashing
    db_user = User(email=user_data.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not (user.hashed_password == form_data.password + "notreallyhashed"):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
