import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from app.main import app
from streamlit_app import fetch_schemes_from_sqlite_db

client = TestClient(app)

print("==========================================================================")
print("TESTING CATEGORY FILTER CASES (FASTAPI REST API & SQLITE DIRECT)")
print("==========================================================================")

def run_case(case_name, params):
    print(f"\n--- {case_name} ---")
    print("Params:", params)
    
    # 1. FastAPI test
    r = client.get("/api/v1/schemes", params=params)
    api_schemes = r.json() if r.status_code == 200 else []
    print(f"  FastAPI Result Count: {len(api_schemes)}")
    for s in api_schemes[:5]:
        print(f"    - [{s.get('code')}] {s.get('title')} | Cat: {s.get('category_name')} | Scope: {s.get('state_district_scope')}")
    if len(api_schemes) > 5:
        print(f"    ... and {len(api_schemes)-5} more")

    # 2. SQLite direct test
    sql_schemes = fetch_schemes_from_sqlite_db(params)
    print(f"  SQLite Result Count: {len(sql_schemes)}")
    for s in sql_schemes[:5]:
        print(f"    - [{s.get('code')}] {s.get('title')} | Cat: {s.get('category_name')} | Scope: {s.get('state_district_scope')}")
    if len(sql_schemes) > 5:
        print(f"    ... and {len(sql_schemes)-5} more")

# Case A: Tamil Nadu + All Categories
run_case("Case A: Tamil Nadu + All Categories", {"state": "Tamil Nadu"})

# Case B: Tamil Nadu + Housing & Urban Development
run_case("Case B: Tamil Nadu + Housing category", {"state": "Tamil Nadu", "category": "Housing & Urban Development"})

# Case C: Tamil Nadu + Healthcare & Insurance
run_case("Case C: Tamil Nadu + Healthcare & Insurance", {"state": "Tamil Nadu", "category": "Healthcare & Insurance"})

# Case D: Reset Filters (No filters)
run_case("Case D: Reset Filters", {})

# Case E: Search + category filter combination ("farmer" + "Agriculture & Farmers Welfare")
run_case("Case E: Search + category filter combination", {"search": "farmer", "category": "Agriculture & Farmers Welfare"})
