import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    await init_db()
    yield

@pytest.mark.asyncio
async def test_register_and_login_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        unique_email = f"citizen_{uuid.uuid4().hex[:6]}@janseva.org"
        
        # 1. Register User
        register_payload = {
            "email": unique_email,
            "password": "SecretPassword123",
            "full_name": "Murugan Tamilson",
            "language_preference": "ta",
            "role": "citizen",
            "district": "Madurai",
            "annual_income": 120000.0
        }
        res = await ac.post("/api/v1/auth/register", json=register_payload)
        assert res.status_code == 200, res.text
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == unique_email
        assert data["user"]["language_preference"] == "ta"
        token = data["access_token"]

        # 2. Get Profile (/me)
        headers = {"Authorization": f"Bearer {token}"}
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["full_name"] == "Murugan Tamilson"

        # 3. Update Profile
        update_payload = {"annual_income": 150000.0, "occupation": "Farmer"}
        put_res = await ac.put("/api/v1/auth/profile", json=update_payload, headers=headers)
        assert put_res.status_code == 200
        assert put_res.json()["annual_income"] == 150000.0
        assert put_res.json()["occupation"] == "Farmer"

        # 4. Login
        login_res = await ac.post("/api/v1/auth/login", json={"email": unique_email, "password": "SecretPassword123"})
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()
