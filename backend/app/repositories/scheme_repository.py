from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.scheme import Scheme, SchemeCategory, SchemeAlias, Document

class SchemeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        search: Optional[str] = None,
        category_id: Optional[str] = None,
        state: Optional[str] = None,
        gender: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        community: Optional[str] = None,
        occupation: Optional[str] = None,
        disability: Optional[bool] = None,
        max_income: Optional[float] = None
    ) -> List[Scheme]:
        query = select(Scheme).options(
            selectinload(Scheme.category),
            selectinload(Scheme.aliases),
            selectinload(Scheme.documents)
        )
        if category_id:
            query = query.where(Scheme.category_id == category_id)
        if state and state not in ["All", "All States / UTs"]:
            if state == "All India" or state == "Central":
                query = query.where(
                    (Scheme.state_district_scope.ilike("%All India%")) | 
                    (Scheme.state_district_scope.ilike("%Central%")) | 
                    (Scheme.state_district_scope.is_(None))
                )
            else:
                state_term = f"%{state.strip()}%"
                query = query.where(
                    (Scheme.state_district_scope.ilike(state_term)) | 
                    (Scheme.state_district_scope.ilike("%All India%")) | 
                    (Scheme.state_district_scope.ilike("%Central%")) | 
                    (Scheme.state_district_scope.is_(None)) | 
                    (Scheme.ministry.ilike(state_term))
                )
        if gender and gender != "All":
            query = query.where((Scheme.gender_restriction == "All") | (Scheme.gender_restriction == gender) | (Scheme.gender_restriction.is_(None)))
        if min_age is not None:
            query = query.where(Scheme.max_age >= min_age)
        if max_age is not None:
            query = query.where(Scheme.min_age <= max_age)
        if community and community != "Select":
            comm_term = f"%{community.strip()}%"
            query = query.where((Scheme.target_community.ilike(comm_term)) | (Scheme.target_community == "All") | (Scheme.target_community.is_(None)))
        if occupation and occupation != "Select":
            occ_term = f"%{occupation.strip()}%"
            query = query.where((Scheme.target_occupation.ilike(occ_term)) | (Scheme.target_occupation == "All") | (Scheme.target_occupation.is_(None)))
        if disability is not None:
            query = query.where(Scheme.disability_required == disability)
        if max_income is not None:
            query = query.where((Scheme.max_income >= max_income) | (Scheme.max_income.is_(None)))
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
