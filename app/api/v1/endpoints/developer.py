from fastapi import APIRouter, Depends, HTTPException
from requests import Session

from app.core.utils import hash_password
from app.db.dependencies import get_db
from app.models.users import User
from app.schemas.user import UserCreate

router = APIRouter(tags=['Developer Auth'])

@router.post("/signup/developer")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        first_Name=user.first_Name,
        last_Name=user.last_Name,
        email=user.email,
        password=hash_password(user.password),
        role_id=4
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created", "role": new_user.role.name, "id": new_user.id,}

