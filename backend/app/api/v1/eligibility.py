from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.eligibility_service import EligibilityService
from app.services.life_event_service import LifeEventService

router = APIRouter(prefix="/eligibility", tags=["Eligibility Meter & Life Event Reasoner"])

class LifeEventRequest(BaseModel):
    prompt: str

class CheckEligibilityRequest(BaseModel):
    age: Optional[int] = 30
    gender: Optional[str] = "female"
    annual_income: Optional[float] = 120000.0
    district: Optional[str] = "Madurai"
    occupation: Optional[str] = "Unorganized Worker"
    disability_status: Optional[bool] = False
    community: Optional[str] = "OBC"
    marital_status: Optional[str] = "Married"
    education_level: Optional[str] = "High School"
    family_members_count: Optional[int] = 4

@router.post("/check")
@router.post("/evaluate")
async def check_eligibility(req: CheckEligibilityRequest, db: AsyncSession = Depends(get_db)):
    service = EligibilityService(db)
    return await service.evaluate_eligibility(req.model_dump())

@router.post("/life-event")
async def analyze_life_event(req: LifeEventRequest, db: AsyncSession = Depends(get_db)):
    service = LifeEventService(db)
    return await service.analyze_life_event(req.prompt)

@router.get("/recommendations")
async def get_user_recommendations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = EligibilityService(db)
    user_params = {
        "age": current_user.age or 30,
        "gender": current_user.gender or "female",
        "annual_income": current_user.annual_income or 120000.0,
        "district": current_user.district or "Madurai",
        "occupation": current_user.occupation or "Worker",
        "disability_status": current_user.disability_status or False,
        "community": current_user.community or "OBC",
        "marital_status": current_user.marital_status or "Married"
    }
    return await service.evaluate_eligibility(user_params)
