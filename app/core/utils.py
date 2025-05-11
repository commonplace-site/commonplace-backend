import os
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
import whisper
from faster_whisper import WhisperModel
import torch
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
    

# Initialize Whisper model with Chinese-optimized settings
model_size = "large-v3"  # Using large-v3 model for better Chinese support
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model = WhisperModel(
    model_size, 
    device=device, 
    compute_type="float16" if device == "cuda" else "float32",
    download_root="./models"  # Specify download location
)

# Initialize jieba for Chinese word segmentation
jieba.initialize()

async def stt_transcribe(
    audio_path: str,
    language: str = "zh-CN",
    punctuate: bool = True,
    speaker_diarization: bool = False,
    word_timestamps: bool = False,
    profanity_filter: bool = True,
    chinese_specific: bool = True
) -> Dict[str, Any]:
    """
    Transcribe audio file using Whisper model with advanced features and Chinese-specific optimizations
    
    Args:
        audio_path: Path to the audio file
        language: Language code (e.g., 'zh-CN' for Chinese)
        punctuate: Whether to add punctuation
        speaker_diarization: Whether to identify different speakers
        word_timestamps: Whether to include word-level timestamps
        profanity_filter: Whether to filter profanity
        chinese_specific: Whether to apply Chinese-specific processing
    
    Returns:
        Dictionary containing transcription results
    """
    try:
        # Load and process audio with Chinese-optimized settings
        segments, info = whisper_model.transcribe(
            audio_path,
            language="zh",  # Force Chinese language
            beam_size=5,
            word_timestamps=word_timestamps,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=100  # Increased padding for Chinese speech
            ),
            condition_on_previous_text=True,  # Better for continuous Chinese speech
            initial_prompt="以下是中文语音转写："  # Chinese prompt for better context
        )

        # Process segments
        transcript_text = ""
        word_timestamps_list = []
        speakers_list = []
        
        for segment in segments:
            # Process Chinese text
            text = segment.text
            if chinese_specific:
                # Apply Chinese-specific text processing
                text = process_chinese_text(text, punctuate)
            
            # Filter profanity if requested
            if profanity_filter:
                text = filter_profanity(text)
            
            transcript_text += text + " "
            
            # Collect word timestamps if requested
            if word_timestamps and segment.words:
                for word in segment.words:
                    word_timestamps_list.append({
                        "word": word.word,
                        "start": word.start,
                        "end": word.end,
                        "confidence": word.probability
                    })
            
            # Basic speaker diarization
            if speaker_diarization:
                speakers_list.append({
                    "text": text,
                    "start": segment.start,
                    "end": segment.end,
                    "speaker": "Speaker 1"
                })

        # Post-process Chinese text
        if chinese_specific:
            transcript_text = post_process_chinese_text(transcript_text)

        return {
            "text": transcript_text.strip(),
            "language": "zh-CN",
            "confidence": info.language_probability,
            "duration": info.duration,
            "word_timestamps": word_timestamps_list if word_timestamps else None,
            "speakers": speakers_list if speaker_diarization else None,
            "chinese_specific": {
                "word_count": len(list(jieba.cut(transcript_text))),
                "char_count": len(transcript_text),
                "has_traditional_chars": bool(re.search(r'[\u4e00-\u9fff]', transcript_text))
            }
        }

    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

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
    

