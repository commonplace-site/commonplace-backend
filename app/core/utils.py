import os
import uuid
from typing import Optional, List, Dict, Set, Union, Any
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.users import User
import speech_recognition as sr
import edge_tts
import asyncio
import tempfile
import jieba
import re

load_dotenv() 

# Load environment variables
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

token_blacklist: Set[str] = set()
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
        if user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user

    return role_checker


def get_current_token(token: str = Depends(oauth2_scheme)):
    if token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token is blacklisted")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return token  # or return payload['sub'] for user info
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_token(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Optionally return payload like user_id, roles, etc.
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")


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
    

# Remove Whisper imports and model initialization
# Replace with speech recognition setup
recognizer = sr.Recognizer()

async def text_to_speech(text: str, language: str = "zh-CN") -> bytes:
    """Convert text to speech using edge-tts"""
    communicate = edge_tts.Communicate(text, language)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        await communicate.save(temp_file.name)
        with open(temp_file.name, "rb") as f:
            audio_data = f.read()
    os.unlink(temp_file.name)
    return audio_data

def speech_to_text(audio_file_path: str, language: str = "zh-CN") -> str:
    """Convert speech to text using Google's speech recognition"""
    with sr.AudioFile(audio_file_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language=language)
            return text
        except sr.UnknownValueError:
            raise HTTPException(status_code=400, detail="Could not understand audio")
        except sr.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Could not request results; {str(e)}")

def process_chinese_text(text: str, punctuate: bool = True) -> str:
    """
    Process Chinese text with specific rules
    """
    # Remove extra spaces
    text = re.sub(r'\s+', '', text)
    
    # Add Chinese punctuation if needed
    if punctuate:
        # Add period if missing
        if not text.endswith(('。', '！', '？', '…')):
            text += '。'
        
        # Add spaces after punctuation for better readability
        text = re.sub(r'([。！？])', r'\1 ', text)
    
    return text

def post_process_chinese_text(text: str) -> str:
    """
    Post-process Chinese text with additional rules
    """
    # Remove duplicate punctuation
    text = re.sub(r'([。！？])\1+', r'\1', text)
    
    # Fix common Chinese transcription errors
    text = text.replace('，', '、')  # Replace comma with Chinese enumeration comma
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    
    return text.strip()

def filter_profanity(text: str) -> str:
    """
    Filter profanity from Chinese text
    """
    # Add Chinese profanity filtering logic here
    # This is a placeholder - implement proper Chinese profanity filtering
    return text
    

