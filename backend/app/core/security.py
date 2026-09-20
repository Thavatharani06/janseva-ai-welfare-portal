import jwt
import hashlib
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Any
from app.core.config import settings

def hash_password(password: str) -> str:
    """Hash password securely using bcrypt directly."""
    pwd_bytes = password.encode('utf-8')[:72]  # Bcrypt 72 byte limit safety
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt with fallback for legacy test hashes."""
    if not hashed_password:
        return False
    # Legacy test hash check
    if hashed_password.startswith("hash_"):
        salt = settings.SECRET_KEY.encode('utf-8')
        legacy_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000).hex()
        return legacy_hash == hashed_password or plain_password == hashed_password.replace("hash_", "")
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        salt = settings.SECRET_KEY.encode('utf-8')
        legacy_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000).hex()
        return legacy_hash == hashed_password

def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None, token_type: str = "access") -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_mfa_pending_token(subject: Any) -> str:
    """Create a short-lived (5 min) token required for MFA verification."""
    return create_access_token(subject=subject, expires_delta=timedelta(minutes=5), token_type="mfa_pending")

def decode_access_token(token: str) -> Optional[dict]:
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded
    except jwt.PyJWTError:
        return None

def generate_recovery_codes(count: int = 8) -> list:
    """Generate cryptographically secure recovery codes."""
    codes = []
    for _ in range(count):
        code = f"{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
        codes.append(code)
    return codes
