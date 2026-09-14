import difflib
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.scheme import Scheme, SchemeAlias

class AliasService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve_scheme_by_query(self, query: str) -> Tuple[Optional[Scheme], float, str]:
        """
        Resolves query to a Scheme using exact match, database alias lookup, or fuzzy similarity.
        Returns: (Scheme, confidence_score, matched_alias)
        """
        clean_query = query.strip().lower()

        # 1. Fetch all schemes with aliases pre-loaded
        result = await self.db.execute(
            select(Scheme).options(selectinload(Scheme.aliases), selectinload(Scheme.category))
        )
        schemes = result.scalars().all()

        best_scheme: Optional[Scheme] = None
        best_score: float = 0.0
        best_matched_term: str = ""

        for scheme in schemes:
            # Check Title, Tamil Title, and Scheme Code
            terms_to_check = [
                (scheme.code.lower(), 1.0),
                (scheme.title.lower(), 0.95),
                ((scheme.title_ta or "").lower(), 0.95)
            ]

            # Add all aliases
            for alias_obj in scheme.aliases:
                terms_to_check.append((alias_obj.alias.lower(), 0.90))

            for term, weight in terms_to_check:
                if not term:
                    continue

                # Exact match
                if clean_query == term or term in clean_query or clean_query in term:
                    similarity = 0.95 if (clean_query == term) else 0.85
                    total_score = similarity * weight
                    if total_score > best_score:
                        best_score = total_score
                        best_scheme = scheme
                        best_matched_term = term
                else:
                    # Fuzzy match using SequenceMatcher
                    ratio = difflib.SequenceMatcher(None, clean_query, term).ratio()
                    total_score = ratio * weight
                    if total_score > 0.65 and total_score > best_score:
                        best_score = total_score
                        best_scheme = scheme
                        best_matched_term = term

        return best_scheme, round(best_score, 2), best_matched_term

    async def add_alias(self, scheme_id: str, alias_text: str, language_code: str = "en") -> SchemeAlias:
        alias = SchemeAlias(scheme_id=scheme_id, alias=alias_text.strip(), language_code=language_code)
        self.db.add(alias)
        await self.db.commit()
        await self.db.refresh(alias)
        return alias
