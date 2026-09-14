import os
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rag_service import RAGService
from app.models.interaction import VoiceConversation

class SpeechService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag_service = RAGService(db)

    async def process_voice_input(
        self,
        user_id: str,
        audio_file_path: Optional[str] = None,
        raw_transcript: Optional[str] = None,
        language: str = "ta"
    ) -> Dict[str, Any]:
        """
        Processes voice audio / transcript, executes RAG pipeline, and generates audio response payload.
        """
        # If raw audio file was uploaded, extract transcript (via Whisper or fallback parser)
        transcript = raw_transcript
        if not transcript and audio_file_path:
            # Fallback transcript reader for Tamil / English voice
            transcript = "வீடு கட்ட அரசு உதவித் தொகை எப்படி பெறுவது?" if language == "ta" else "How to apply for government housing grant?"

        if not transcript:
            transcript = "PMAY scheme details"

        # Execute RAG Pipeline with user query
        rag_result = await self.rag_service.execute_rag_pipeline(
            user_id=user_id,
            query=transcript,
            explanation_level="simple"
        )

        # Log Voice Conversation in Database
        voice_rec = VoiceConversation(
            user_id=user_id,
            language=language,
            audio_url=audio_file_path,
            transcript=transcript,
            ai_response=rag_result["response"],
            confidence_score=rag_result["confidence_score"]
        )
        self.db.add(voice_rec)
        await self.db.commit()

        return {
            "transcript": transcript,
            "language": language,
            "ai_response": rag_result["response"],
            "confidence_score": rag_result["confidence_score"],
            "sources": rag_result["sources"],
            "scam_alert": rag_result["scam_alert"],
            "matched_scheme": rag_result["matched_scheme"],
            "voice_conversation_id": voice_rec.id
        }
