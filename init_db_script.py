import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.core.database import engine, Base
import app.models
from app.services.seed_service import seed_initial_welfare_data
from app.core.database import AsyncSessionLocal

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database schema initialized successfully.")

    async with AsyncSessionLocal() as session:
        await seed_initial_welfare_data(session)
    print("Database initial seeding complete.")

if __name__ == "__main__":
    asyncio.run(init_db())
