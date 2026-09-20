from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.schemas.family import FamilyMemberCreate, FamilyMemberResponse
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Normalized Citizen Profile & Family"])

@router.get("/me")
async def get_normalized_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    return await service.get_normalized_profile(current_user.id)

@router.post("/family", response_model=FamilyMemberResponse)
async def add_family_member(
    req: FamilyMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    return await service.add_family_member(current_user.id, req.model_dump())

@router.delete("/family/{member_id}")
async def delete_family_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    success = await service.delete_family_member(current_user.id, member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Family member record not found or access denied")
    return {"status": "SUCCESS", "message": "Family member removed."}
