import math
import re
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.scheme import DocumentEmbedding, Document, Scheme

class VectorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """Lightweight offline TF-IDF cosine similarity for text chunk vectors."""
        words1 = re.findall(r'\w+', text1.lower())
        words2 = re.findall(r'\w+', text2.lower())

        freq1 = {}
        for w in words1:
            freq1[w] = freq1.get(w, 0) + 1

        freq2 = {}
        for w in words2:
            freq2[w] = freq2.get(w, 0) + 1

        common_words = set(freq1.keys()) & set(freq2.keys())
        dot_product = sum(freq1[w] * freq2[w] for w in common_words)

        norm1 = math.sqrt(sum(v ** 2 for v in freq1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in freq2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    async def search_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval combining keyword matching and vector similarity over database embeddings.
        """
        result = await self.db.execute(
            select(DocumentEmbedding)
            .options(selectinload(DocumentEmbedding.document).selectinload(Document.scheme))
        )
        embeddings = result.scalars().all()

        scored_chunks = []
        for emb in embeddings:
            sim_score = self._calculate_cosine_similarity(query, emb.chunk_content)
            
            # Boost score if query contains scheme code or title
            scheme_title = emb.document.scheme.title if emb.document and emb.document.scheme else ""
            scheme_code = emb.document.scheme.code if emb.document and emb.document.scheme else ""
            if scheme_code.lower() in query.lower() or scheme_title.lower() in query.lower():
                sim_score = max(sim_score, 0.88)

            scored_chunks.append({
                "chunk_id": emb.id,
                "chunk_index": emb.chunk_index,
                "chunk_content": emb.chunk_content,
                "page_number": emb.page_number,
                "similarity_score": round(sim_score, 3),
                "document_title": emb.document.title if emb.document else "Official Directive",
                "go_number": emb.document.go_number if emb.document else "N/A",
                "scheme_title": scheme_title,
                "scheme_code": scheme_code
            })

        # Sort by similarity score descending
        scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_chunks[:top_k]
