import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from app.main import app

def test_category_query():
    client = TestClient(app)
    
    print("--- 1. Testing GET /api/v1/schemes?state=Tamil%20Nadu ---")
    r1 = client.get("/api/v1/schemes?state=Tamil%20Nadu")
    print(f"Status: {r1.status_code}, Count: {len(r1.json())}")
    
    print("\n--- 2. Testing GET /api/v1/schemes?state=Tamil%20Nadu&category=Housing%20%26%20Urban%20Development ---")
    r2 = client.get("/api/v1/schemes?state=Tamil%20Nadu&category=Housing%20%26%20Urban%20Development")
    print(f"Status: {r2.status_code}, Count: {len(r2.json())}")
    if r2.json():
        for s in r2.json():
            print("  Matched:", s.get("code"), s.get("title"), "| state:", s.get("state_district_scope"))
    else:
        print("  Returned 0 schemes!")

    print("\n--- 3. Testing GET /api/v1/schemes?category=Housing%20%26%20Urban%20Development ---")
    r3 = client.get("/api/v1/schemes?category=Housing%20%26%20Urban%20Development")
    print(f"Status: {r3.status_code}, Count: {len(r3.json())}")
    for s in r3.json():
        print("  Matched:", s.get("code"), s.get("title"), "| state:", s.get("state_district_scope"))

if __name__ == "__main__":
    test_category_query()
