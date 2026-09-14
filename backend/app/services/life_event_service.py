from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.scheme import Scheme

LIFE_EVENT_MAPPINGS = [
    {
        "keywords": ["husband passed away", "widow", "death certificate", "husband died", "கணவர் இறந்துவிட்டார்", "கைம்பெண்", "died"],
        "event_title": "Loss of Spouse / Widow Welfare",
        "recommended_schemes": ["KMT", "Widow Pension Scheme", "National Family Benefit Scheme (NFBS)", "Legal Aid Services"],
        "advice": "We offer our deepest condolences. As a widow, you are eligible for monthly Widow Pension, one-time Rs. 20,000 NFBS death grant, free legal aid, and priority housing."
    },
    {
        "keywords": ["daughter", "engineering", "college", "higher education", "girl child", "மகள்", "புதுமைப் பெண்"],
        "event_title": "Higher Education for Girl Child",
        "recommended_schemes": ["PUDHUMAI-PENN", "Post-Matric Scholarship", "Education Loan Interest Subsidy", "Moovalur Ramamirtham Scheme"],
        "advice": "Congratulations on your daughter's admission! Under the Pudhumai Penn scheme, she receives Rs. 1,000 monthly grant throughout her college degree if she attended government school."
    },
    {
        "keywords": ["lost my job", "unemployed", "need work", "no income", "வேலை இல்லை", "தொழில் கடன்", "jobless"],
        "event_title": "Employment & Skill Development",
        "recommended_schemes": ["MGNREGA 100 Days Work", "TN Unemployed Youth Employment Generation (UYEGP)", "PM Employment Generation Programme"],
        "advice": "You are eligible for 100 days guaranteed wage employment under MGNREGA or up to Rs. 15 Lakhs self-employment business loan with 25% government subsidy."
    }
]

class LifeEventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_life_event(self, prompt: str) -> Dict[str, Any]:
        clean_prompt = prompt.lower()
        matched_event = None

        for mapping in LIFE_EVENT_MAPPINGS:
            for kw in mapping["keywords"]:
                if kw in clean_prompt:
                    matched_event = mapping
                    break
            if matched_event:
                break

        if not matched_event:
            matched_event = {
                "event_title": "General Life Transition Support",
                "recommended_schemes": ["PMAY-U", "PM-KISAN", "PM-JAY", "KMT"],
                "advice": "Based on your situation, government welfare programs provide financial assistance, healthcare coverage up to Rs. 5 Lakhs, and subsidized housing."
            }

        # Fetch actual scheme details from DB for recommended scheme codes
        result = await self.db.execute(select(Scheme))
        all_schemes = result.scalars().all()

        recommended_scheme_objects = []
        for s in all_schemes:
            if any(rec.lower() in s.code.lower() or rec.lower() in s.title.lower() for rec in matched_event["recommended_schemes"]):
                recommended_scheme_objects.append({
                    "id": s.id,
                    "code": s.code,
                    "title": s.title,
                    "title_ta": s.title_ta,
                    "simple_summary": s.simple_summary
                })

        return {
            "life_event_prompt": prompt,
            "event_title": matched_event["event_title"],
            "guidance_advice": matched_event["advice"],
            "recommended_schemes": recommended_scheme_objects
        }
