import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- 1. Testing GET /api/v1/schemes/categories ---")
r_cats = client.get("/api/v1/schemes/categories")
print("Categories endpoint status:", r_cats.status_code)
print("Categories JSON:", r_cats.json())

print("\n--- 2. Testing GET /api/v1/schemes?state=Tamil+Nadu&category=Housing+%26+Urban+Development ---")
r_housing = client.get("/api/v1/schemes?state=Tamil%20Nadu&category=Housing%20%26%20Urban%20Development")
print("Housing status:", r_housing.status_code)
print("Housing count:", len(r_housing.json()))
for item in r_housing.json():
    print(" ", item.get("code"), item.get("title"))

print("\n--- 3. Testing GET /api/v1/schemes?state=Tamil+Nadu&category=Housing ---")
r_h1 = client.get("/api/v1/schemes?state=Tamil%20Nadu&category=Housing")
print("Partial 'Housing' count:", len(r_h1.json()))

print("\n--- 4. Testing GET /api/v1/schemes?state=Tamil+Nadu&category=Housing+and+Urban+Development ---")
r_h2 = client.get("/api/v1/schemes?state=Tamil%20Nadu&category=Housing%20and%20Urban%20Development")
print("With 'and' instead of '&' count:", len(r_h2.json()))

print("\n--- 5. Testing GET /api/v1/schemes?state=Tamil+Nadu&category_id=Housing%20%26%20Urban%20Development ---")
r_h3 = client.get("/api/v1/schemes?state=Tamil%20Nadu&category_id=Housing%20%26%20Urban%20Development")
print("With category_id count:", len(r_h3.json()))
