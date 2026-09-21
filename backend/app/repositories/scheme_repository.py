from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
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
        if category_id and category_id.strip() not in ["All Categories", "Select", "All"]:
            c_clean = category_id.strip()
            cat_terms = {c_clean}
            if "&" in c_clean:
                cat_terms.add(c_clean.replace("&", "and"))
            if " and " in c_clean:
                cat_terms.add(c_clean.replace(" and ", " & "))
            
            cat_conditions = []
            for term in cat_terms:
                cat_term = f"%{term}%"
                cat_conditions.extend([
                    Scheme.category_id == term,
                    Scheme.category_name.ilike(cat_term),
                    SchemeCategory.name.ilike(cat_term)
                ])
            query = query.outerjoin(Scheme.category).where(or_(*cat_conditions))
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
        if search and search.strip():
            s_raw = search.strip()
            s_lower = s_raw.lower()
            search_term = f"%{s_lower}%"
            import re
            
            stop_words = {
                "i", "a", "an", "the", "in", "on", "at", "to", "for", "of", "or", "and", "is", "it", "am", "are", "be", "by", "my", "me", "we", "us", "he", "she", "do", "no", "so", "if", "as",
                "need", "want", "looking", "help", "with", "scheme", "schemes", "government", "govt", "support", "assistance",
                "எனக்கு", "வேண்டும்", "உதவி", "திட்டம்", "அரசு", "ஒரு", "மற்றும்", "உள்ளது",
                "मुझे", "चाहिए", "सहायता", "योजना", "सरकारी", "एक", "और", "का", "की", "के", "में", "से", "हूँ", "है", "लिए"
            }
            raw_tokens = [w.lower() for w in re.findall(r'[^\s,.!?\-\"\']+', s_raw)]
            words = [w for w in raw_tokens if len(w) >= 2 and w not in stop_words]
            
            # Multilingual Domain Concepts Mapping with agglutinative suffix support for valid tokens
            concept_keywords = []
            valid_words = [w for w in raw_tokens if len(w) <= 20]
            s_combined = " ".join(valid_words)
            
            # Education domain
            if s_combined and any(k in s_combined for k in ["education", "study", "student", "scholarship", "school", "college", "degree", "கல்வி", "படிப்பு", "பள்ளி", "கல்லூரி", "மாணவ", "शिक्षा", "पढ़ाई", "छात्रवृत्ति", "स्कूल"]):
                concept_keywords.extend(["education", "scholarship", "school", "college", "student", "matric", "samagra", "poshan", "pudhumai"])
            # Housing domain
            if s_combined and any(k in s_combined for k in ["housing", "house", "home", "building", "construction", "pmay", "shelter", "வீடு", "குடியிருப்பு", "ஆவாஸ்", "घर", "मकान", "आवास", "गृह"]):
                concept_keywords.extend(["housing", "awas", "house", "green house", "home", "building"])
            # Agriculture / Farmer domain
            if s_combined and any(k in s_combined for k in ["farmer", "agriculture", "crop", "kisan", "cultivation", "power", "solar", "விவசாயி", "விவசாயம்", "பயிர்", "உழவர்", "किसान", "कृषि", "फसल"]):
                concept_keywords.extend(["farmer", "agriculture", "kisan", "crop", "fasal", "uzhavar", "rythu", "kalia"])
            # Healthcare domain
            if s_combined and any(k in s_combined for k in ["health", "hospital", "insurance", "medical", "treatment", "medicine", "dialysis", "மருத்துவம்", "சுகாதாரம்", "மருத்துவமனை", "स्वास्थ्य", "अस्पताल", "इलाज", "बीमा"]):
                concept_keywords.extend(["health", "insurance", "ayushman", "maruthuvam", "medical", "hospital", "dialysis"])
            # Social Welfare / Pension domain
            if s_combined and any(k in s_combined for k in ["pension", "elderly", "old age", "widow", "disabled", "disability", "ஓய்வூதியம்", "பரிசு", "पेंशन", "वृद्धावस्था"]):
                concept_keywords.extend(["pension", "old age", "widow", "disability", "disabled", "maintenance"])
            # Women & Girl Child domain
            if s_combined and any(k in s_combined for k in ["women", "girl", "mother", "female", "maternity", "marriage", "மகளிர்", "பெண்", "பெண்கள்", "திருமணம்", "महिला", "बेटी", "स्त्री", "विवाह"]):
                concept_keywords.extend(["women", "girl", "matru", "magalir", "maternity", "marriage", "kanyashree", "sukanya", "ladli"])
            # Business / Employment / MSME domain
            if s_combined and any(k in s_combined for k in ["business", "loan", "entrepreneur", "employment", "skill", "vendor", "job", "வேலை", "தொழில்", "கடன்", "रोजगार", "नौकरी", "व्यापार", "ऋण"]):
                concept_keywords.extend(["employment", "skill", "mudra", "svanidhi", "entrepreneur", "business", "unemployed", "vishwakarma"])

            search_conditions = [
                Scheme.title.ilike(search_term),
                Scheme.title_ta.ilike(search_term),
                Scheme.code.ilike(search_term),
                Scheme.legal_summary.ilike(search_term),
                Scheme.simple_summary.ilike(search_term),
                Scheme.benefits_summary.ilike(search_term),
                Scheme.eligibility_description.ilike(search_term)
            ]
            all_search_words = words + concept_keywords
            for w in all_search_words:
                w_pattern = f"%{w}%"
                search_conditions.extend([
                    Scheme.title.ilike(w_pattern),
                    Scheme.title_ta.ilike(w_pattern),
                    Scheme.code.ilike(w_pattern),
                    Scheme.category_name.ilike(w_pattern),
                    Scheme.legal_summary.ilike(w_pattern),
                    Scheme.simple_summary.ilike(w_pattern),
                    Scheme.benefits_summary.ilike(w_pattern),
                    Scheme.eligibility_description.ilike(w_pattern)
                ])
            query = query.where(or_(*search_conditions))

        result = await self.db.execute(query)
        schemes = result.scalars().all()

        if search and search.strip():
            s_lower = search.strip().lower()
            import re
            raw_eval_tokens = [w.lower() for w in re.findall(r'[^\s,.!?\-\"\']+', s_lower)]
            q_words = [w for w in raw_eval_tokens if len(w) >= 2 and w not in stop_words]
            all_eval_words = q_words + concept_keywords
            
            def calculate_relevance(s):
                score = 0.0
                title_lower = (s.title or "").lower()
                code_lower = (s.code or "").lower()
                cat_lower = (s.category_name or "").lower()
                desc_lower = f"{s.legal_summary or ''} {s.simple_summary or ''} {s.benefits_summary or ''} {s.eligibility_description or ''}".lower()
                
                if s_lower in code_lower or s_lower in title_lower:
                    score += 15.0
                
                for qw in all_eval_words:
                    if qw in code_lower: score += 6.0
                    if qw in title_lower: score += 5.0
                    if qw in cat_lower: score += 4.0
                    if qw in desc_lower: score += 2.0
                return score
            
            schemes = list(schemes)
            schemes.sort(key=calculate_relevance, reverse=True)

        return schemes

    async def get_by_id(self, scheme_id: str) -> Optional[Scheme]:
        query = select(Scheme).options(
            selectinload(Scheme.category),
            selectinload(Scheme.aliases),
            selectinload(Scheme.documents),
            selectinload(Scheme.eligibility_rules)
        ).where(
            (Scheme.id == scheme_id) | 
            (Scheme.code.ilike(scheme_id)) | 
            (Scheme.code.ilike(f"%{scheme_id}%"))
        )
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
