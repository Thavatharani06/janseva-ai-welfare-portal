from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.auth import get_optional_current_user
from app.models.user import User
from app.services.electricity_service import ElectricityService

router = APIRouter(prefix="/electricity", tags=["Electricity Service & Benefit Eligibility"])

@router.get("/benefits")
async def get_electricity_benefits():
    service = ElectricityService()
    return {
        "service": "Electricity",
        "benefits_catalog": service.benefits,
        "official_source": "Government of Tamil Nadu — Energy Department & Handlooms Department"
    }

@router.post("/evaluate")
async def evaluate_electricity(
    req: Dict[str, Any],
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ElectricityService()
    profile = {}
    if current_user:
        profile = {
            "state": "Tamil Nadu",
            "district": current_user.district or "Madurai",
            "occupation": current_user.occupation or "Worker",
            "annual_income": current_user.annual_income or 120000.0
        }
    
    # Merge overrides from request body
    consumer_type = req.get("consumer_type")
    occupation = req.get("occupation") or profile.get("occupation")
    state = req.get("state") or profile.get("state") or "Tamil Nadu"

    return service.evaluate_eligibility(
        profile=profile,
        consumer_type=consumer_type,
        occupation=occupation,
        state=state,
        target_benefit_id=req.get("target_benefit_id")
    )
