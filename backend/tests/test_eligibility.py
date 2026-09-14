import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db, AsyncSessionLocal
from app.services.seed_service import seed_initial_welfare_data

@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_initial_welfare_data(session)
    yield

@pytest.mark.asyncio
async def test_life_event_reasoning_and_eligibility_meter():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Test Life Event Reasoning: "My daughter is joining engineering"
        life_res = await ac.post("/api/v1/eligibility/life-event", json={
            "prompt": "My daughter is joining engineering college after 12th"
        })
        assert life_res.status_code == 200
        life_data = life_res.json()
        assert "Girl Child" in life_data["event_title"] or "Education" in life_data["event_title"]
        assert len(life_data["recommended_schemes"]) > 0

        # 2. Test Life Event Reasoning: "My husband passed away"
        widow_res = await ac.post("/api/v1/eligibility/life-event", json={
            "prompt": "My husband passed away recently, need financial support"
        })
        assert widow_res.status_code == 200
        widow_data = widow_res.json()
        assert "Widow" in widow_data["event_title"] or "Spouse" in widow_data["event_title"]

        # 3. Test Interactive Eligibility Meter Check
        elig_res = await ac.post("/api/v1/eligibility/check", json={
            "age": 35,
            "gender": "female",
            "annual_income": 120000.0,
            "district": "Madurai",
            "occupation": "Unorganized Worker",
            "disability_status": False,
            "community": "OBC",
            "marital_status": "Married"
        })
        assert elig_res.status_code == 200
        elig_data = elig_res.json()
        assert "high_priority" in elig_data["recommendations"]
        assert len(elig_data["recommendations"]["high_priority"]) > 0
        # KMT (Magalir Urimai) should be high priority for 35yo female with 1.2L income
        high_codes = [s["code"] for s in elig_data["recommendations"]["high_priority"]]
        assert "KMT" in high_codes or "PMAY-U" in high_codes
