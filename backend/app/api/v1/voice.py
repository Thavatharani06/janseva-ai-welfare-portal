from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.auth import get_optional_current_user
from app.models.user import User
from app.services.speech_service import SpeechService

router = APIRouter(prefix="/voice", tags=["Multilingual Voice AI Assistant"])

@router.post("/process")
@router.post("/process-voice")
async def process_voice(
    file: Optional[UploadFile] = File(None),
    raw_transcript: Optional[str] = Form(None),
    language: str = Form("ta"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    speech_service = SpeechService(db)
    audio_bytes = None
    file_path = None
    if file:
        audio_bytes = await file.read()
        file_path = f"uploads/voice_{file.filename}"

    user_id = current_user.id if current_user else "guest-user"
    return await speech_service.process_voice_input(
        user_id=user_id,
        audio_bytes=audio_bytes,
        audio_file_path=file_path,
        raw_transcript=raw_transcript,
        language=language
    )
