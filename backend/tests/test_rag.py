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
async def test_rag_query_scam_detection_and_citations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        unique_email = f"rag_{uuid.uuid4().hex[:6]}@janseva.org"
        reg = await ac.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "Password123",
            "full_name": "RAG User",
            "language_preference": "ta"
        })
        assert reg.status_code == 200, reg.text
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Test normal RAG query with exact alias "Magalir Urimai"
        rag_res = await ac.post("/api/v1/rag/query", json={
            "query": "How to get Magalir Urimai monthly 1000 rupees in Tamil Nadu?",
            "explanation_level": "simple"
        }, headers=headers)
        assert rag_res.status_code == 200
        data = rag_res.json()
        assert "confidence_score" in data
        assert data["confidence_score"] >= 0.70
        assert len(data["sources"]) > 0
        assert "go_number" in data["sources"][0]
        assert data["matched_scheme"] is not None
        assert data["matched_scheme"]["code"] == "KMT"

        # 2. Test Scam Warning Detection
        scam_res = await ac.post("/api/v1/rag/query", json={
            "query": "Agent says pay money 500 rupees to get PMAY housing scheme",
            "explanation_level": "simple"
        }, headers=headers)
        assert scam_res.status_code == 200
        scam_data = scam_res.json()
        assert scam_data["scam_alert"] is not None
        assert scam_data["scam_alert"]["scam_flagged"] is True
        assert "1100" in [h["number"] for h in scam_data["scam_alert"]["official_helplines"]]

        # 3. Test Chat History retrieval
        hist_res = await ac.get("/api/v1/rag/history", headers=headers)
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert len(history) == 2
