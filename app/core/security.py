from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECURITY_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300
REFRESH_TOKEN_EXPIRE_DAYS = 1

# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = 60

# Security headers middleware
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password validation
def validate_password_strength(password: str) -> bool:
    """
    Validate password strength
    Returns True if password meets requirements
    """
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False
    return True

# Token validation
def validate_token(token: str) -> bool:
    """
    Validate token format and expiration
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
        exp = payload.get("exp")
        if exp is None:
            return False
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            return False
        return True
    except (JWTError, ValidationError):
        return False

# Security middleware
async def security_middleware(request, call_next):
    """
    Add security headers to all responses
    """
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

# Rate limiting
class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    def is_rate_limited(self, client_id: str) -> bool:
        now = datetime.utcnow()
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(self.requests[client_id]) >= RATE_LIMIT_PER_MINUTE:
            return True
        
        self.requests[client_id].append(now)
        return False

rate_limiter = RateLimiter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id
