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
async def test_scheme_listing_and_alias_resolution():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch categories
        cat_res = await ac.get("/api/v1/schemes/categories")
        assert cat_res.status_code == 200
        categories = cat_res.json()
        assert len(categories) >= 4

        # 2. List schemes
        scheme_res = await ac.get("/api/v1/schemes")
        assert scheme_res.status_code == 200
        schemes = scheme_res.json()
        assert len(schemes) >= 5

        # 3. Test Tamil Alias Search: "வீடு கட்ட உதவி" -> PMAY-U
        alias_ta = await ac.get("/api/v1/schemes/alias/search?alias=வீடு கட்ட உதவி")
        assert alias_ta.status_code == 200
        data_ta = alias_ta.json()
        assert data_ta["matched_scheme"]["code"] == "PMAY-U"
        assert data_ta["confidence"] >= 0.85

        # 4. Test Acronym Alias Search: "PMAY" -> PMAY-U
        alias_pmay = await ac.get("/api/v1/schemes/alias/search?alias=PMAY")
        assert alias_pmay.status_code == 200
        assert alias_pmay.json()["matched_scheme"]["code"] == "PMAY-U"

        # 5. Test Tamil Magalir Urimai Alias Search: "மகளிர் உரிமைத் தொகை" -> KMT
        alias_kmt = await ac.get("/api/v1/schemes/alias/search?alias=மகளிர் உரிமைத் தொகை")
        assert alias_kmt.status_code == 200
        assert alias_kmt.json()["matched_scheme"]["code"] == "KMT"
