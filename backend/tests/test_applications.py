import uuid
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
async def test_guided_welfare_journey_and_form_generation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register Citizen
        user_email = f"citizen_{uuid.uuid4().hex[:6]}@janseva.org"
        reg = await ac.post("/api/v1/auth/register", json={
            "email": user_email,
            "password": "Password123",
            "full_name": "Kavitha M",
            "district": "Madurai",
            "annual_income": 120000.0
        })
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get PMAY Scheme ID
        schemes_res = await ac.get("/api/v1/schemes?search=PMAY")
        scheme = schemes_res.json()[0]

        # 3. Create Application
        create_res = await ac.post("/api/v1/applications", json={"scheme_id": scheme["id"]}, headers=headers)
        assert create_res.status_code == 200
        app_data = create_res.json()
        app_id = app_data["id"]
        assert app_data["journey_step"] == "eligibility_verified"
        assert len(app_data["missing_docs"]) > 0

        # 4. Generate PDF Form
        pdf_res = await ac.post(f"/api/v1/applications/{app_id}/generate-pdf", json={
            "address": "45 West Car Street, Madurai",
            "family_count": 4
        }, headers=headers)
        assert pdf_res.status_code == 200
        pdf_data = pdf_res.json()
        assert "pdf_url" in pdf_data
        assert pdf_data["journey_step"] == "ready_for_submission"

        # 5. Verify Application Details
        detail_res = await ac.get(f"/api/v1/applications/{app_id}", headers=headers)
        assert detail_res.status_code == 200
        assert detail_res.json()["pdf_url"] is not None
