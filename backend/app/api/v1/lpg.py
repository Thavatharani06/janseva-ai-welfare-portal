from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.schemas.lpg import LPGBindRequest, LPGStatusResponse
from app.services.lpg_service import LPGService

router = APIRouter(prefix="/lpg", tags=["LPG & Subsidy Government Service"])

@router.get("/status", response_model=LPGStatusResponse)
async def get_lpg_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = LPGService(db)
    return await service.get_connection_status(current_user.id)

@router.post("/bind")
async def bind_lpg_consumer(
    req: LPGBindRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = LPGService(db)
    return await service.bind_lpg_consumer(
        user_id=current_user.id,
        consumer_id=req.consumer_id,
        provider=req.provider
    )

@router.post("/disconnect")
async def disconnect_lpg(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = LPGService(db)
    return await service.disconnect_lpg(current_user.id)
