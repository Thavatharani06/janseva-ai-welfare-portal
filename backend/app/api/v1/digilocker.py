from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.schemas.digilocker import (
    DigiLockerConnectUrlResponse,
    DigiLockerCallbackRequest,
    DigiLockerStatusResponse
)
from app.services.digilocker_service import DigiLockerService

router = APIRouter(prefix="/digilocker", tags=["DigiLocker Government Document Requester"])

@router.get("/connect-url", response_model=DigiLockerConnectUrlResponse)
async def get_connect_url(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DigiLockerService(db)
    return service.generate_authorization_url(current_user.id)

@router.get("/status", response_model=DigiLockerStatusResponse)
async def get_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DigiLockerService(db)
    return await service.get_connection_status(current_user.id)

@router.post("/callback")
async def handle_callback(
    req: DigiLockerCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DigiLockerService(db)
    return await service.process_oauth_callback(
        user_id=current_user.id,
        code=req.code,
        state=req.state
    )

@router.post("/disconnect")
async def disconnect(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DigiLockerService(db)
    return await service.disconnect(current_user.id)
