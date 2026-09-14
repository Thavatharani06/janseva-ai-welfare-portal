import asyncio
from app.core.database import init_db, AsyncSessionLocal
from app.services.seed_service import seed_initial_welfare_data

async def main():
    print("Initializing database tables...")
    await init_db()
    
    print("Seeding initial welfare schemes and admin profile...")
    async with AsyncSessionLocal() as session:
        await seed_initial_welfare_data(session)
        
    print("SUCCESS: Database Initialized and Seeded Successfully!")

if __name__ == "__main__":
    asyncio.run(main())
