import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from app.core.database import AsyncSessionLocal
from app.repositories.scheme_repository import SchemeRepository

async def test_queries():
    async with AsyncSessionLocal() as db:
        repo = SchemeRepository(db)
        queries = [
            'education scheme',
            'I need housing support',
            'எனக்கு வீடு கட்ட அரசு உதவி வேண்டும்',
            'मुझे शिक्षा के लिए सरकारी योजना चाहिए'
        ]
        for q in queries:
            res = await repo.get_all(search=q)
            q_safe = q.encode('ascii', errors='replace').decode('ascii')
            print(f"Query: '{q_safe}' -> Found {len(res)} matching schemes:")
            for s in res[:4]:
                s_safe = f"  - [{s.code}] {s.title} ({s.category_name})".encode('ascii', errors='replace').decode('ascii')
                print(s_safe)
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_queries())
