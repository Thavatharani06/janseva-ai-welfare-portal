from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserResponse, Token
from app.core.security import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register_user(self, user_create: UserCreate) -> Token:
        existing = await self.user_repo.get_by_email(user_create.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        user_dict = user_create.model_dump()
        raw_password = user_dict.pop("password")
        user_dict["hashed_password"] = hash_password(raw_password)

        user = await self.user_repo.create(user_dict)
        access_token = create_access_token(subject=user.id)
        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    async def authenticate_user(self, credentials: UserLogin) -> Token:
        user = await self.user_repo.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
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
