import os
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid

from fastapi.security import OAuth2PasswordBearer
from app.db.dependencies import get_db
from app.models.users import User
import openai
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(db: Session = Depends(lambda: get_db()), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")
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

# OpenAI Clients
openai.api_key = OPENAI_API_KEY

async def tts_generate(text: str):
    response = await openai.Audio.acreate(
        model="tts-1",
        input=text,
        voice="nova"
    )
    return response

async def stt_transcribe(file_path: str):
    with open(file_path, "rb") as f:
        response = await openai.Audio.atranscribe(
            model="whisper-1",
            file=f
        )
    return response["text"]

async def generate_avatar_speech(text: str) -> str:
    # This is a mocked URL, replace with real Synesthesia API call
    return f"https://api.synesthesia.io/fake_avatar_video/{uuid.uuid4()}.mp4"