import os
import uuid
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.application import Application, UploadedDocument, GeneratedForm
from app.models.scheme import Scheme
from app.models.user import User
from app.services.ocr_service import OCRService
from app.services.form_service import FormService

class JourneyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_application(self, user_id: str, scheme_id: str) -> Application:
        scheme_result = await self.db.execute(select(Scheme).where(Scheme.id == scheme_id))
        scheme = scheme_result.scalars().first()
        if not scheme:
            raise ValueError("Scheme not found")

        required_docs = scheme.required_documents or ["Aadhaar Card", "Income Certificate"]

        app = Application(
            user_id=user_id,
            scheme_id=scheme_id,
            status="draft",
            journey_step="eligibility_verified",
            missing_docs=required_docs,
            form_data={}
        )
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        return app

    async def handle_document_upload(
        self,
        application_id: str,
        document_type: str,
        file_name: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Uploads user document, runs OCR, updates missing document checklist, and advances journey step.
        """
        result = await self.db.execute(
            select(Application)
            .options(selectinload(Application.scheme), selectinload(Application.uploaded_documents))
            .where(Application.id == application_id)
        )
        app = result.scalars().first()
        if not app:
            raise ValueError("Application not found")

        # Extract text via OCR
        ocr_text = OCRService.extract_text_from_file(file_path)

        uploaded_doc = UploadedDocument(
            application_id=application_id,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path,
            ocr_extracted_text=ocr_text,
            is_verified=True
        )
        self.db.add(uploaded_doc)

        # Update Missing Documents Checklist
        required_docs = app.scheme.required_documents or []
        uploaded_types = [d.document_type.lower() for d in app.uploaded_documents] + [document_type.lower()]
        
        remaining_missing = []
        for req in required_docs:
            if not any(req.lower() in up_type or up_type in req.lower() for up_type in uploaded_types):
                remaining_missing.append(req)

        app.missing_docs = remaining_missing
        if not remaining_missing:
            app.status = "documents_complete"
            app.journey_step = "ready_for_form_generation"
        else:
            app.status = "documents_pending"
            app.journey_step = "upload_missing_documents"

        await self.db.commit()

        return {
            "application_id": application_id,
            "uploaded_doc_id": uploaded_doc.id,
            "document_type": document_type,
            "ocr_extracted_snippet": ocr_text[:150],
            "missing_docs": remaining_missing,
            "journey_step": app.journey_step
        }

    async def generate_application_form(self, application_id: str, form_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-fills application form fields, generates PDF, and advances journey to 'ready_for_submission'.
        """
        result = await self.db.execute(
            select(Application)
            .options(selectinload(Application.scheme), selectinload(Application.user), selectinload(Application.uploaded_documents))
            .where(Application.id == application_id)
        )
        app = result.scalars().first()
        if not app:
            raise ValueError("Application not found")

        tracking_id = f"JANSEVA-{app.scheme.code}-{uuid.uuid4().hex[:6].upper()}"
        pdf_filename = f"generated_form_{application_id}.pdf"
        pdf_dir = os.path.join("downloads", "forms")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        form_data_merged = {
            "tracking_id": tracking_id,
            "submission_date": "2026-07-21",
            "verified_docs": [d.document_type for d in app.uploaded_documents] or ["Aadhaar Card"],
            **form_inputs
        }

        FormService.generate_official_application_pdf(
            output_pdf_path=pdf_path,
            scheme_name=app.scheme.title,
            scheme_code=app.scheme.code,
            applicant_name=app.user.full_name,
            applicant_email=app.user.email,
            district=app.user.district or "Madurai",
            annual_income=app.user.annual_income or 120000.0,
            form_fields=form_data_merged
        )

        gen_form = GeneratedForm(
            application_id=application_id,
            pdf_path=f"/downloads/forms/{pdf_filename}",
            form_fields=form_data_merged
        )
        self.db.add(gen_form)

        app.status = "form_generated"
        app.journey_step = "ready_for_submission"
        app.form_data = form_data_merged

        await self.db.commit()

        return {
            "application_id": application_id,
            "tracking_id": tracking_id,
            "pdf_url": f"/downloads/forms/{pdf_filename}",
            "journey_step": app.journey_step,
            "form_fields": form_data_merged
        }
