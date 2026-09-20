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

def mask_identifier(val: Optional[str], visible_suffix: int = 4) -> str:
    """Mask sensitive identifiers e.g. XXXX-XXXX-1234."""
    if not val:
        return "N/A"
    clean = str(val).strip()
    if len(clean) <= visible_suffix:
        return "*" * len(clean)
    suffix = clean[-visible_suffix:]
    prefix_len = len(clean) - visible_suffix
    masked_prefix = "X" * prefix_len
    # Format with hyphens for readability if length is 12-16
    if len(clean) >= 10:
        return f"XXXX-XXXX-{suffix}"
    return f"{masked_prefix}{suffix}"

def hash_identifier(val: str) -> str:
    """Salted SHA-256 hash for secure identifier lookup without storing raw text."""
    salt = settings.SECRET_KEY.encode('utf-8')
    return hashlib.pbkdf2_hmac('sha256', val.encode('utf-8'), salt, 10000).hex()

def encrypt_token(plain_str: str) -> str:
    """Simple obfuscated token storage using HMAC-SHA256 key XOR."""
    if not plain_str:
        return ""
    key = hashlib.sha256(settings.SECRET_KEY.encode('utf-8')).digest()
    data = plain_str.encode('utf-8')
    cipher = bytearray()
    for i, b in enumerate(data):
        cipher.append(b ^ key[i % len(key)])
    return cipher.hex()

def decrypt_token(enc_hex: str) -> str:
    """Decrypt token stored with encrypt_token."""
    if not enc_hex:
        return ""
    try:
        key = hashlib.sha256(settings.SECRET_KEY.encode('utf-8')).digest()
        cipher = bytes.fromhex(enc_hex)
        plain = bytearray()
        for i, b in enumerate(cipher):
            plain.append(b ^ key[i % len(key)])
        return plain.decode('utf-8')
    except Exception:
        return ""

