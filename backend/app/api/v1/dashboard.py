from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.application import Application
from app.models.interaction import ChatHistory, Notification
from app.services.eligibility_service import EligibilityService

router = APIRouter(prefix="/dashboard", tags=["Citizen Dashboard & AI Memory Context"])

@router.get("/stats", response_model=Dict[str, Any])
@router.get("/metrics", response_model=Dict[str, Any])
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch User Applications
    app_res = await db.execute(
        select(Application)
        .options(selectinload(Application.scheme), selectinload(Application.generated_form))
        .where(Application.user_id == current_user.id)
    )
    applications = app_res.scalars().all()

    # 2. Fetch Chat History
    chat_res = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(5)
    )
    recent_chats = chat_res.scalars().all()

    # 3. Fetch Notifications
    notif_res = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    notifications = notif_res.scalars().all()

    # 4. Compute AI Recommendations
    elig_service = EligibilityService(db)
    user_params = {
        "age": current_user.age or 32,
        "gender": current_user.gender or "female",
        "annual_income": current_user.annual_income or 120000.0,
        "district": current_user.district or "Madurai",
        "occupation": current_user.occupation or "Worker",
        "disability_status": current_user.disability_status or False,
        "community": current_user.community or "OBC",
        "marital_status": current_user.marital_status or "Married"
    }
    eval_res = await elig_service.evaluate_eligibility(user_params)

    # 5. Extract Missing Documents
    all_missing = set()
    for a in applications:
        if a.missing_docs:
            for doc in a.missing_docs:
                all_missing.add(doc)

    return {
        "user_profile": {
            "full_name": current_user.full_name,
            "email": current_user.email,
            "language_preference": current_user.language_preference,
            "district": current_user.district or "Madurai",
            "annual_income": current_user.annual_income or 120000.0,
            "role": current_user.role
        },
        "applications": [
            {
                "id": a.id,
                "scheme_title": a.scheme.title if a.scheme else "Welfare Scheme",
                "scheme_code": a.scheme.code if a.scheme else "SCHEME",
                "status": a.status,
                "journey_step": a.journey_step,
                "pdf_url": a.generated_form.pdf_path if a.generated_form else None
            } for a in applications
        ],
        "eligible_schemes_count": len(eval_res["recommendations"]["high_priority"]),
        "high_priority_schemes": eval_res["recommendations"]["high_priority"],
        "missing_documents": list(all_missing),
        "recent_queries": [
            {
                "query": c.query,
                "explanation_level": c.explanation_level,
                "created_at": c.created_at
            } for c in recent_chats
        ],
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read
            } for n in notifications
        ]
    }
