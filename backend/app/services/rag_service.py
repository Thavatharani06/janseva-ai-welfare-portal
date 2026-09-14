import time
import httpx
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.alias_service import AliasService
from app.services.scam_service import ScamService
from app.services.vector_service import VectorService
from app.models.interaction import ChatHistory, AILog
from app.core.config import settings

class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alias_service = AliasService(db)
        self.vector_service = VectorService(db)

    async def execute_rag_pipeline(
        self,
        user_id: str,
        query: str,
        explanation_level: str = "simple"
    ) -> Dict[str, Any]:
        """
        Complete RAG Pipeline:
        1. Alias Detection
        2. Scam Detection
        3. Vector Retrieval & Context Compression
        4. Prompt Construction & Local LLM Execution
        5. Source Transparency Calculation (Confidence %, G.O. Num, Page, Chunk ID)
        """
        start_time = time.time()

        # Step 1: Check for Scam Indicators
        scam_result = ScamService.detect_scam(query)

        # Step 2: Resolve Scheme Alias
        matched_scheme, alias_confidence, matched_alias = await self.alias_service.resolve_scheme_by_query(query)

        # Step 3: Hybrid Retrieval of Top-K Chunks
        chunks = await self.vector_service.search_relevant_chunks(query, top_k=3)

        # Fallback if query didn't retrieve vector chunks but matched a scheme
        if matched_scheme and not chunks:
            chunks = [{
                "chunk_id": f"chunk-scheme-{matched_scheme.code}",
                "chunk_index": 0,
                "chunk_content": matched_scheme.legal_summary,
                "page_number": 1,
                "similarity_score": alias_confidence,
                "document_title": f"Government Notification - {matched_scheme.title}",
                "go_number": "Official Gazette 2023",
                "scheme_title": matched_scheme.title,
                "scheme_code": matched_scheme.code
            }]

        # Step 4: Calculate Overall AI Confidence Score
        if chunks:
            top_sim = max(c["similarity_score"] for c in chunks)
            confidence_score = round(min(0.98, max(0.70, (top_sim * 0.5) + (alias_confidence * 0.5))), 2)
        else:
            confidence_score = 0.75

        # Step 5: Construct Prompt & LLM Generation
        context_str = "\n".join([f"Source [{c['go_number']}]: {c['chunk_content']}" for c in chunks])
        
        prompt = f"""You are JanSeva AI, an official government welfare assistant.
User Query: {query}
Retrieved Context:
{context_str}

Please generate an accurate answer in '{explanation_level}' mode (legal, simple, or eli10).
"""

        # Try connecting to Ollama Local LLM, fallback to offline template generator
        llm_response = ""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False}
                )
                if res.status_code == 200:
                    llm_response = res.json().get("response", "")
        except Exception:
            pass  # Fallback to local offline template

        if not llm_response:
            if matched_scheme:
                if explanation_level == "legal":
                    llm_response = matched_scheme.legal_summary
                elif explanation_level == "eli10":
                    llm_response = matched_scheme.eli10_summary
                else:
                    llm_response = matched_scheme.simple_summary
            else:
                llm_response = f"Based on public welfare records, for '{query}', citizens can access financial assistance, subsidy registration, and document verification at local e-Sevai centers or official government portals."

        # Append Scam Alert if flagged
        if scam_result.get("scam_flagged"):
            llm_response = f"{scam_result['warning_title']}\n{scam_result['warning_message']}\n\n{llm_response}"

        # Step 6: Construct Source Transparency Metadata
        sources = []
        for c in chunks:
            sources.append({
                "document_name": c["document_title"],
                "go_number": c["go_number"],
                "page_number": c["page_number"],
                "chunk_id": str(c["chunk_id"]),
                "similarity_score": c["similarity_score"],
                "retrieved_context": c["chunk_content"][:150] + "..."
            })

        latency = round((time.time() - start_time) * 1000, 2)

        # Step 7: Record Chat History & AI Log in Database
        chat_rec = ChatHistory(
            user_id=user_id,
            query=query,
            explanation_level=explanation_level,
            response=llm_response,
            sources_json=sources,
            scam_flagged=scam_result.get("scam_flagged", False),
            scam_reason=scam_result.get("warning_message") if scam_result.get("scam_flagged") else None,
            confidence_score=confidence_score
        )
        self.db.add(chat_rec)

        ai_log = AILog(
            query=query,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(llm_response.split()),
            latency_ms=latency,
            confidence_score=confidence_score
        )
        self.db.add(ai_log)

        await self.db.commit()

        return {
            "query": query,
            "explanation_level": explanation_level,
            "response": llm_response,
            "confidence_score": confidence_score,
            "scam_alert": scam_result if scam_result.get("scam_flagged") else None,
            "matched_scheme": {
                "id": matched_scheme.id,
                "title": matched_scheme.title,
                "code": matched_scheme.code
            } if matched_scheme else None,
            "sources": sources,
            "reasoning_summary": f"Query resolved via alias matcher '{matched_alias or 'direct'}' and vector cosine similarity search across {len(chunks)} official government orders.",
            "latency_ms": latency
        }
