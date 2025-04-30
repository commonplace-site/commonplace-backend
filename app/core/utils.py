# import os
# from typing import Optional, List, Dict
# from datetime import datetime, timedelta
# import uuid
# from passlib.context import CryptContext
# from fastapi.security import OAuth2PasswordBearer
# from app.db.dependencies import get_db
# from app.models.users import User
# import openai
# from fastapi import Depends, HTTPException
# from jose import JWTError, jwt
# from sqlalchemy.orm import Session
# from fastapi import Security
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError,jwt

# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM", "HS256")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")
# pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

# def hash_password(password:str):
#     return pwd_context.hash(password)
# def verify_password(plain_password,hashed_password):
#     return
# pwd_context.verify (plain_password,hash_password)

# def create_access_token(data:dict):
#     to_encode=data.copy()
#     expire=datetime.utcnow()+timedelta(hours=1)
#     to_encode.update({"exp":expire})
#     return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    



# def get_current_user(token:str=Depends(oauth2_scheme)):
#     try: 
#         payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
#         return{"username":payload.get("sub"),"role":
#                payload.get("role")} 
#     except JWTError:
#         raise HTTPException(status_code=400, detail="Username already exists")


# def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid credentials",
#         headers={"WWW-Authenticate": "Bearer"}
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     user = db.query(User).filter(User.email == email).first()
#     if user is None:
#         raise credentials_exception

#     return user


# def role_required(required_role:str):
#         def role_checker(user=Depends(get_current_user)):
#             if user ["role"]!=required_role:raise 
#             HTTPException(status_code=403,
#         detail="Not enough permissions" )
#             return user 
#         return role_checker 
#     # @app.get("/")


# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# OpenAI Clients
# openai.api_key = OPENAI_API_KEY

# async def tts_generate(text: str):
#     response = await openai.Audio.acreate(
#         model="tts-1",
#         input=text,
#         voice="nova"
#     )
#     return response

# async def stt_transcribe(file_path: str):
#     with open(file_path, "rb") as f:
#         response = await openai.Audio.atranscribe(
#             model="whisper-1",
#             file=f
#         )
#     return response["text"]

# async def generate_avatar_speech(text: str) -> str:
#     # This is a mocked URL, replace with real Synesthesia API call
#     return f"https://api.synesthesia.io/fake_avatar_video/{uuid.uuid4()}.mp4"













import os
from typing import Optional, List, Dict, Union
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.users import User

# Load environment variables
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Password hashing and verification
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Token generation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Get current user from token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


# Role-based access (multi-role support)
def role_required(allowed_roles: Union[str, List[str]]):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user

    return role_checker



def create_reset_token(email:str):
    expire = datetime.utcnow()+timedelta(minutes=30)
    data={"sub":email,"exp":expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.JWTError:
        return None