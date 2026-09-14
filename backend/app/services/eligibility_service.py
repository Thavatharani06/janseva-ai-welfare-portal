from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.scheme import Scheme
from app.models.user import User

class EligibilityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_eligibility(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates user demographics against all scheme eligibility rules.
        Params: age, gender, annual_income, district, occupation, disability_status, community, marital_status
        """
        result = await self.db.execute(select(Scheme))
        schemes = result.scalars().all()

        age = params.get("age", 30)
        gender = (params.get("gender") or "all").lower()
        income = float(params.get("annual_income") or 0.0)
        occupation = (params.get("occupation") or "").lower()
        disability = bool(params.get("disability_status", False))
        community = (params.get("community") or "General").lower()
        marital_status = (params.get("marital_status") or "").lower()

        high_priority = []
        medium_priority = []
        optional_priority = []

        for s in schemes:
            score = 100
            reasons_eligible = []
            reasons_rejected = []

            # 1. Income Check
            if s.max_income is not None:
                if income <= s.max_income:
                    reasons_eligible.append(f"Annual income ₹{income:,.0f} is within limit of ₹{s.max_income:,.0f}.")
                else:
                    score -= 40
                    reasons_rejected.append(f"Annual income ₹{income:,.0f} exceeds maximum limit ₹{s.max_income:,.0f}.")

            # 2. Age Check
            if s.min_age <= age <= s.max_age:
                reasons_eligible.append(f"Age {age} falls between {s.min_age} and {s.max_age} years.")
            else:
                score -= 30
                reasons_rejected.append(f"Age {age} outside scheme range {s.min_age}-{s.max_age} years.")

            # 3. Gender Check
            if s.gender_restriction and s.gender_restriction.lower() != "all":
                if gender == s.gender_restriction.lower():
                    reasons_eligible.append(f"Gender matches '{s.gender_restriction}' criterion.")
                else:
                    score -= 40
                    reasons_rejected.append(f"Scheme restricted to {s.gender_restriction} applicants.")

            # 4. Target Occupation Check
            if s.target_occupation and s.target_occupation.lower() != "all":
                if s.target_occupation.lower() in occupation:
                    reasons_eligible.append(f"Occupation matches '{s.target_occupation}'.")
                else:
                    score -= 15
                    reasons_rejected.append(f"Scheme prioritizes {s.target_occupation} applicants.")

            item = {
                "scheme_id": s.id,
                "code": s.code,
                "title": s.title,
                "title_ta": s.title_ta,
                "eligibility_percentage": max(0, score),
                "is_eligible": score >= 70,
                "reasons_eligible": reasons_eligible,
                "reasons_rejected": reasons_rejected,
                "required_documents": s.required_documents or [],
                "simple_summary": s.simple_summary
            }

            if score >= 85:
                high_priority.append(item)
            elif score >= 60:
                medium_priority.append(item)
            else:
                optional_priority.append(item)

        return {
            "evaluated_user_profile": params,
            "total_schemes_evaluated": len(schemes),
            "recommendations": {
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "optional": optional_priority
            }
        }
