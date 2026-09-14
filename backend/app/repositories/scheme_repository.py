from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.scheme import Scheme, SchemeCategory, SchemeAlias, Document

class SchemeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, search: Optional[str] = None, category_id: Optional[str] = None) -> List[Scheme]:
        query = select(Scheme).options(
            selectinload(Scheme.category),
            selectinload(Scheme.aliases),
            selectinload(Scheme.documents)
        )
        if category_id:
            query = query.where(Scheme.category_id == category_id)
        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                (Scheme.title.ilike(search_term)) |
                (Scheme.title_ta.ilike(search_term)) |
                (Scheme.code.ilike(search_term)) |
                (Scheme.legal_summary.ilike(search_term))
            )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, scheme_id: str) -> Optional[Scheme]:
        query = select(Scheme).options(
            selectinload(Scheme.category),
            selectinload(Scheme.aliases),
            selectinload(Scheme.documents),
            selectinload(Scheme.eligibility_rules)
        ).where(Scheme.id == scheme_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_categories(self) -> List[SchemeCategory]:
        result = await self.db.execute(select(SchemeCategory))
        return result.scalars().all()

    async def create_scheme(self, scheme_data: dict) -> Scheme:
        scheme = Scheme(**scheme_data)
        self.db.add(scheme)
        await self.db.commit()
        await self.db.refresh(scheme)
        return scheme
