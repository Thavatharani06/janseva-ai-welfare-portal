from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.application import Application
from app.services.journey_service import JourneyService

router = APIRouter(prefix="/applications", tags=["Smart Application Assistant & Form Generator"])

class CreateApplicationRequest(BaseModel):
    scheme_id: str

@router.post("", response_model=Dict[str, Any])
async def create_application(
    req: CreateApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = JourneyService(db)
    app = await service.create_application(user_id=current_user.id, scheme_id=req.scheme_id)
    return {
        "id": app.id,
        "scheme_id": app.scheme_id,
        "status": app.status,
        "journey_step": app.journey_step,
        "missing_docs": app.missing_docs
    }

@router.get("", response_model=List[Dict[str, Any]])
async def list_user_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.scheme), selectinload(Application.generated_form))
        .where(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
    )
    apps = result.scalars().all()
    return [
        {
            "id": a.id,
            "scheme_title": a.scheme.title if a.scheme else "Welfare Scheme",
            "scheme_code": a.scheme.code if a.scheme else "SCHEME",
            "status": a.status,
            "journey_step": a.journey_step,
            "missing_docs": a.missing_docs,
            "pdf_url": a.generated_form.pdf_path if a.generated_form else None,
            "created_at": a.created_at
        }
        for a in apps
    ]

@router.get("/{application_id}")
async def get_application_details(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Application)
        .options(
            selectinload(Application.scheme),
            selectinload(Application.uploaded_documents),
            selectinload(Application.generated_form)
        )
        .where(Application.id == application_id, Application.user_id == current_user.id)
    )
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return {
        "id": app.id,
        "scheme": {
            "id": app.scheme.id,
            "title": app.scheme.title,
            "code": app.scheme.code,
            "required_documents": app.scheme.required_documents
        },
        "status": app.status,
        "journey_step": app.journey_step,
        "missing_docs": app.missing_docs,
        "uploaded_documents": [
            {
                "id": doc.id,
                "document_type": doc.document_type,
                "file_name": doc.file_name,
                "is_verified": doc.is_verified
            } for doc in app.uploaded_documents
        ],
        "pdf_url": app.generated_form.pdf_path if app.generated_form else None,
        "form_data": app.form_data
    }

@router.post("/{application_id}/upload-document")
async def upload_document(
    application_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = JourneyService(db)
    file_path = f"uploads/{application_id}_{file.filename}"
    return await service.handle_document_upload(
        application_id=application_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path
    )

@router.post("/{application_id}/generate-pdf")
async def generate_pdf_form(
    application_id: str,
    form_inputs: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = JourneyService(db)
    return await service.generate_application_form(application_id, form_inputs)
