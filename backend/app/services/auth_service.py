import pyotp
import qrcode
import io
import base64
import json
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreate, UserLogin, UserUpdate, UserResponse, Token,
    MFASetupResponse, MFAVerifyRequest, MFALoginResponse
)
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_mfa_pending_token, decode_access_token, generate_recovery_codes
)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    def _generate_qr_code_base64(self, uri: str) -> str:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    async def register_user(self, user_create: UserCreate) -> MFASetupResponse:
        existing = await self.user_repo.get_by_email(user_create.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        user_dict = user_create.model_dump()
        raw_password = user_dict.pop("password")
        user_dict["hashed_password"] = hash_password(raw_password)
        
        # Generate TOTP Secret & Recovery Codes
        mfa_secret = pyotp.random_base32()
        recovery_codes = generate_recovery_codes(8)
        
        user_dict["mfa_secret"] = mfa_secret
        user_dict["is_mfa_enabled"] = False
        user_dict["mfa_recovery_codes"] = json.dumps(recovery_codes)
        user_dict["is_onboarded"] = False

        user = await self.user_repo.create(user_dict)
        
        # Provisioning URI & QR Code
        totp = pyotp.TOTP(mfa_secret)
        provision_uri = totp.provisioning_uri(name=user.email, issuer_name="JanSeva AI Welfare")
        qr_code_url = self._generate_qr_code_base64(provision_uri)
        
        temp_token = create_mfa_pending_token(subject=user.id)
        
        return MFASetupResponse(
            temp_token=temp_token,
            secret=mfa_secret,
            qr_code_url=qr_code_url,
            recovery_codes=recovery_codes
        )

    async def confirm_mfa_setup(self, verify_req: MFAVerifyRequest) -> Token:
        payload = decode_access_token(verify_req.temp_token)
        if not payload or payload.get("type") != "mfa_pending":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired MFA setup token"
            )
        
        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.mfa_secret:
            raise HTTPException(status_code=404, detail="User not found or MFA secret missing")

        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(verify_req.totp_code.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 6-digit TOTP code. Please check your authenticator app."
            )
        
        # Mark MFA enabled
        await self.user_repo.update(user, {"is_mfa_enabled": True})
        
        access_token = create_access_token(subject=user.id)
        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    async def authenticate_user(self, credentials: UserLogin) -> MFALoginResponse:
        user = await self.user_repo.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # All users require TOTP MFA
        mfa_token = create_mfa_pending_token(subject=user.id)
        return MFALoginResponse(
            mfa_required=True,
            mfa_token=mfa_token,
            user=UserResponse.model_validate(user)
        )

    async def verify_mfa_login(self, mfa_token: str, totp_code: str) -> Token:
        payload = decode_access_token(mfa_token)
        if not payload or payload.get("type") != "mfa_pending":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired MFA session token"
            )
        
        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        clean_code = totp_code.strip()
        is_valid = False

        # Check TOTP 6-digit code
        if user.mfa_secret:
            totp = pyotp.TOTP(user.mfa_secret)
            is_valid = totp.verify(clean_code)

        # Check Recovery Code if TOTP failed
        if not is_valid and user.mfa_recovery_codes:
            try:
                rec_codes = json.loads(user.mfa_recovery_codes)
                if clean_code.upper() in rec_codes:
                    is_valid = True
                    # Remove used recovery code
                    rec_codes.remove(clean_code.upper())
                    await self.user_repo.update(user, {"mfa_recovery_codes": json.dumps(rec_codes)})
            except Exception:
                pass

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA authentication code"
            )
        
        access_token = create_access_token(subject=user.id)
        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    async def update_profile(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        updated_user = await self.user_repo.update(user, update_data.model_dump(exclude_unset=True))
        return UserResponse.model_validate(updated_user)
