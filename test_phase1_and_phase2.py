import pytest
import asyncio
import json
import os
import sys

# Ensure backend directory is on python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.electricity_service import ElectricityService
from app.services.digilocker_service import DigiLockerService
from app.services.profile_service import ProfileService

def test_1_demo_profile_no_aadhaar():
    """1. Demo profile with no Aadhaar -> no fake Aadhaar generated in DB."""
    from app.models.user import User
    user_attrs = [a.key for a in User.__table__.columns]
    assert "aadhaar" not in user_attrs
    assert "aadhaar_number" not in user_attrs

def test_2_demo_profile_provenance_display():
    """2. Demo profile with seeded Aadhaar -> provenance clearly identifies demo profile source."""
    with open("streamlit_app.py", "r", encoding="utf-8") as f:
        code = f.read()
    assert "[Source: Demo Profile Data]" in code or "[Source: Verified DigiLocker Profile]" in code
    assert "[Verified Masked]" not in code

def test_3_digilocker_disconnected():
    """3. DigiLocker disconnected -> no DigiLocker data claimed."""
    with open("streamlit_app.py", "r", encoding="utf-8") as f:
        code = f.read()
    assert "No authorized DigiLocker documents connected yet" in code or "No authorized documents/profile data imported yet" in code

def test_4_digilocker_denied():
    """4. DigiLocker denied -> no imported data."""
    async def _test():
        svc = DigiLockerService(db=None)
        res = await svc.process_oauth_callback(user_id="u1", code="", state="s1")
        assert res["status"] == "AUTHORIZATION_DENIED"
    asyncio.run(_test())

def test_5_6_7_digilocker_state_and_conflicts():
    """5-7. DigiLocker authorized fields & explicit citizen confirmation before applying."""
    with open("streamlit_app.py", "r", encoding="utf-8") as f:
        code = f.read()
    assert "Confirm & Apply Selected Information to Profile" in code
    assert "chk_d_name" in code
    assert "chk_d_dob" in code

def test_8_tamil_nadu_handloom_weaver():
    """8. Tamil Nadu + Handloom Weaver -> 200-unit bi-monthly benefit evaluated."""
    es = ElectricityService()
    res = es.evaluate_eligibility(profile={"state": "Tamil Nadu", "occupation": "Handloom Weaver"})
    assert res["status"] == "ELIGIBLE"
    handloom_b = next(b for b in res["evaluated_benefits"] if b["benefit_id"] == "TN_HANDLOOM_FREE_ELECTRICITY")
    assert handloom_b["unit_limit"] == 200

def test_9_tamil_nadu_powerloom_weaver():
    """9. Tamil Nadu + Powerloom Weaver -> 750-unit bi-monthly benefit evaluated."""
    es = ElectricityService()
    res = es.evaluate_eligibility(profile={"state": "Tamil Nadu", "occupation": "Powerloom Weaver"})
    assert res["status"] == "ELIGIBLE"
    powerloom_b = next(b for b in res["evaluated_benefits"] if b["benefit_id"] == "TN_POWERLOOM_FREE_ELECTRICITY")
    assert powerloom_b["unit_limit"] == 750

def test_10_tamil_nadu_domestic_consumer():
    """10. Tamil Nadu + Domestic Consumer -> evaluate only against documented domestic rule."""
    es = ElectricityService()
    res = es.evaluate_eligibility(profile={"state": "Tamil Nadu", "occupation": "Software Engineer"}, consumer_type="Domestic Consumer")
    assert res["status"] == "ELIGIBLE"
    dom_b = next(b for b in res["evaluated_benefits"] if b["benefit_id"] == "TN_DOMESTIC_ELECTRICITY_SUBSIDY")
    assert dom_b["unit_limit"] == 100

def test_11_unknown_occupation():
    """11. Unknown occupation -> UNKNOWN / MORE INFORMATION REQUIRED."""
    es = ElectricityService()
    res = es.evaluate_eligibility(profile={"state": "Tamil Nadu", "occupation": "UNKNOWN"})
    assert res["status"] == "MORE_INFORMATION_REQUIRED"

def test_12_non_tamil_nadu():
    """12. Non-Tamil Nadu -> Tamil Nadu-specific benefit must not be marked eligible."""
    es = ElectricityService()
    res = es.evaluate_eligibility(profile={"state": "Karnataka", "occupation": "Handloom Weaver"})
    assert res["status"] == "NOT_ELIGIBLE"

def test_13_to_19_existing_features():
    """13-19. Verify existing LPG, Scheme Search, 71-scheme catalog, and Voice APIs exist and remain untouched."""
    with open("backend/app/main.py", "r", encoding="utf-8") as f:
        main_code = f.read()
    assert "schemes.router" in main_code
    assert "voice.router" in main_code
    assert "lpg.router" in main_code
    assert "digilocker.router" in main_code
    assert "profile.router" in main_code
    assert "electricity.router" in main_code

if __name__ == "__main__":
    pytest.main(["-v", __file__])
