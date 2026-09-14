import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.test_auth import test_register_and_login_flow

async def run_all():
    print("Running Auth Vertical Slice Integration Test...")
    await test_register_and_login_flow()
    print("✅ AUTH VERTICAL SLICE PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_all())
