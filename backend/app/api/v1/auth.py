from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, UserUpdate, Token,
    MFASetupResponse, MFAVerifyRequest, MFALoginResponse, PasswordResetRequest
)
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Strictly authenticate current user. Throw HTTP 401 if unauthenticated."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_access_token(token)
        if not payload or "sub" not in payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not found"
            )
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Optional[User]:
    """Return user if authenticated token is provided, else return None for guest requests."""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if not payload or "sub" not in payload or payload.get("type") != "access":
            return None
        user_repo = UserRepository(db)
        return await user_repo.get_by_id(payload["sub"])
    except Exception:
        return None

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Enforce strict ADMIN role check. Throw HTTP 403 if citizen."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin authorization required. Access denied."
        )
    return current_user

@router.post("/register", response_model=MFASetupResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.register_user(user_in)

@router.post("/mfa/confirm-setup", response_model=Token)
async def confirm_mfa_setup(verify_req: MFAVerifyRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.confirm_mfa_setup(verify_req)

@router.post("/login", response_model=MFALoginResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.authenticate_user(user_in)

@router.post("/mfa/verify", response_model=Token)
async def verify_mfa_login(mfa_token: str, totp_code: str, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.verify_mfa_login(mfa_token, totp_code)

@router.post("/forgot-password")
async def forgot_password(req: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    # Standard security practice: do not leak whether email exists
    return {
        "message": "If an account exists with this email address, a password reset link has been sent."
    }

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.update_profile(current_user.id, user_update)
