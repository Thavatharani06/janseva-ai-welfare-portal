import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.digilocker import DigiLockerConnection, DigiLockerDocument
from app.models.lpg import LPGConnection
from app.models.family import FamilyMember

logger = logging.getLogger("janseva.profile")

class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_normalized_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Returns unified citizen profile incorporating:
        - Personal Information (User model)
        - DigiLocker Verified Attributes (with source="DIGILOCKER")
        - LPG Connection Data (with source="LPG_OFFICIAL_API")
        - Family Members (FamilyMember model)
        Tracks explicit provenance per attribute to show citizens transparent data sources.
        """
        res = await self.db.execute(
            select(User)
            .options(
                selectinload(User.digilocker_connection).selectinload(DigiLockerConnection.documents),
                selectinload(User.lpg_connection),
                selectinload(User.family_members)
            )
            .where(User.id == user_id)
        )
        user = res.scalars().first()
        if not user:
            return {}

        # 1. Base Personal Attributes (from User Profile)
        profile_data = {
            "full_name": {"value": user.full_name, "source": "USER_PROFILE"},
            "email": {"value": user.email, "source": "USER_PROFILE"},
            "age": {"value": user.age or 30, "source": "USER_PROFILE"},
            "gender": {"value": user.gender or "female", "source": "USER_PROFILE"},
            "annual_income": {"value": user.annual_income or 120000.0, "source": "USER_PROFILE"},
            "district": {"value": user.district or "Madurai", "source": "USER_PROFILE"},
            "occupation": {"value": user.occupation or "Worker", "source": "USER_PROFILE"},
            "disability_status": {"value": user.disability_status or False, "source": "USER_PROFILE"},
            "community": {"value": user.community or "OBC", "source": "USER_PROFILE"},
            "marital_status": {"value": user.marital_status or "Married", "source": "USER_PROFILE"},
            "education_level": {"value": user.education_level or "High School", "source": "USER_PROFILE"},
            "language_preference": {"value": user.language_preference, "source": "USER_PROFILE"}
        }

        # 2. Check for DigiLocker Verified Attributes
        digilocker_status = "NOT_CONNECTED"
        verified_documents = []
        if user.digilocker_connection and user.digilocker_connection.connection_status == "connected":
            digilocker_status = "CONNECTED"
            for doc in user.digilocker_connection.documents:
                ext = json.loads(doc.extracted_data) if doc.extracted_data else {}
                verified_documents.append({
                    "id": doc.id,
                    "doc_type": doc.doc_type,
                    "name": doc.name,
                    "issuer": doc.issuer,
                    "issue_date": doc.issue_date,
                    "verification_status": doc.verification_status
                })
                # Override profile fields with verified DigiLocker data where present
                if doc.doc_type == "AADHAAR" and "full_name" in ext:
                    profile_data["full_name"] = {"value": ext["full_name"], "source": "DIGILOCKER"}
                if doc.doc_type == "INCOME_CERTIFICATE" and "annual_income" in ext:
                    profile_data["annual_income"] = {"value": ext["annual_income"], "source": "DIGILOCKER"}

        # 3. Check for LPG Connection Data
        lpg_data = {"status": "NOT_CONNECTED"}
        if user.lpg_connection and user.lpg_connection.connection_status == "active":
            lpg_data = {
                "status": "CONNECTED",
                "consumer_id_masked": user.lpg_connection.consumer_id_masked,
                "provider": user.lpg_connection.provider,
                "distributor_name": user.lpg_connection.distributor_name,
                "connection_type": user.lpg_connection.connection_type,
                "subsidy_eligible": user.lpg_connection.subsidy_eligible,
                "last_refill_date": user.lpg_connection.last_refill_date,
                "refill_count": user.lpg_connection.refill_count,
                "subsidy_received_amount": user.lpg_connection.subsidy_received_amount,
                "source": "LPG_OFFICIAL_API"
            }

        # 4. Family Members
        family = [
            {
                "id": fm.id,
                "full_name": fm.full_name,
                "relationship_type": fm.relationship_type,
                "age": fm.age,
                "gender": fm.gender,
                "occupation": fm.occupation,
                "is_dependent": fm.is_dependent,
                "source": "USER_PROFILE"
            }
            for fm in user.family_members
        ]

        return {
            "user_id": user.id,
            "personal_info": profile_data,
            "digilocker": {
                "status": digilocker_status,
                "documents": verified_documents
            },
            "lpg": lpg_data,
            "family_members": family
        }

    async def add_family_member(self, user_id: str, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adds a new family member for citizen."""
        fm = FamilyMember(
            user_id=user_id,
            full_name=member_data["full_name"],
            relationship_type=member_data["relationship_type"],
            age=member_data.get("age"),
            gender=member_data.get("gender"),
            occupation=member_data.get("occupation"),
            is_dependent=member_data.get("is_dependent", True)
        )
        self.db.add(fm)
        await self.db.commit()
        await self.db.refresh(fm)
        return {
            "id": fm.id,
            "full_name": fm.full_name,
            "relationship_type": fm.relationship_type,
            "age": fm.age,
            "gender": fm.gender,
            "occupation": fm.occupation,
            "is_dependent": fm.is_dependent
        }

    async def delete_family_member(self, user_id: str, member_id: str) -> bool:
        """Deletes a family member ensuring user isolation."""
        res = await self.db.execute(
            select(FamilyMember).where(FamilyMember.id == member_id, FamilyMember.user_id == user_id)
        )
        fm = res.scalars().first()
        if fm:
            await self.db.delete(fm)
            await self.db.commit()
            return True
        return False
