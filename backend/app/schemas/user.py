from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    language_preference: str = "ta"
    role: str = "citizen"
    age: Optional[int] = None
    gender: Optional[str] = None
    annual_income: Optional[float] = None
    district: Optional[str] = None
    occupation: Optional[str] = None
    disability_status: Optional[bool] = False
    community: Optional[str] = None
    marital_status: Optional[str] = None
    education_level: Optional[str] = None
    family_members_count: Optional[int] = 1
    property_owner: Optional[bool] = False
    is_mfa_enabled: bool = False
    is_onboarded: bool = False

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    language_preference: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    annual_income: Optional[float] = None
    district: Optional[str] = None
    occupation: Optional[str] = None
    disability_status: Optional[bool] = None
    community: Optional[str] = None
    marital_status: Optional[str] = None
    education_level: Optional[str] = None
    family_members_count: Optional[int] = None
    property_owner: Optional[bool] = None
    is_onboarded: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MFASetupResponse(BaseModel):
    temp_token: str
    secret: str
    qr_code_url: str
    recovery_codes: List[str]

class MFAVerifyRequest(BaseModel):
    temp_token: str
    totp_code: str

class MFALoginResponse(BaseModel):
    mfa_required: bool = False
    mfa_token: Optional[str] = None
    access_token: Optional[str] = None
    user: Optional[UserResponse] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

