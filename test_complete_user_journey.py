import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import time
import pyotp
import json
from fastapi.testclient import TestClient
from app.main import app

def run_user_journey_test():
    print("=" * 70)
    print("JANSEVA AI - COMPLETE END-TO-END USER JOURNEY VERIFICATION")
    print("=" * 70)

    client = TestClient(app)

    # Step 1: NEW USER REGISTRATION
    unique_email = f"journey_user_{int(time.time())}@janseva.gov.in"
    print(f"\n1. REGISTERING NEW USER ({unique_email})...")
    reg_payload = {
        "email": unique_email,
        "password": "Password123!",
        "full_name": "Ramesh Swaminathan",
        "language_preference": "ta"
    }
    r = client.post("/api/v1/auth/register", json=reg_payload)
    assert r.status_code == 200, f"Registration failed: {r.text}"
    reg_data = r.json()
    secret = reg_data["secret"]
    temp_token = reg_data["temp_token"]
    print("   [OK] User registered with MFA secret.")

    # Confirm MFA Setup
    totp = pyotp.TOTP(secret)
    r = client.post("/api/v1/auth/mfa/confirm-setup", json={"temp_token": temp_token, "totp_code": totp.now()})
    assert r.status_code == 200, f"MFA setup failed: {r.text}"
    token_data = r.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("   [OK] MFA setup confirmed. JWT Access Token obtained.")

    # Step 2: LOGIN
    print("\n2. LOGIN & AUTHENTICATED SESSION VERIFICATION...")
    r = client.post("/api/v1/auth/login", json={"email": unique_email, "password": "Password123!"})
    assert r.status_code == 200
    mfa_token = r.json()["mfa_token"]
    r = client.post(f"/api/v1/auth/mfa/verify?mfa_token={mfa_token}&totp_code={totp.now()}")
    assert r.status_code == 200
    access_token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("   [OK] Login & TOTP MFA challenge passed.")

    # Step 3: PROFILE SETUP
    print("\n3. CREATING / UPDATING USER PROFILE...")
    profile_payload = {
        "full_name": "Ramesh Swaminathan",
        "age": 22,
        "gender": "male",
        "district": "Madurai",
        "occupation": "Student",
        "annual_income": 150000.0,
        "disability_status": False,
        "community": "OBC",
        "marital_status": "Single",
        "language_preference": "ta"
    }
    r = client.put("/api/v1/auth/profile", json=profile_payload, headers=headers)
    assert r.status_code == 200, f"Profile update failed: {r.text}"
    user_prof = r.json()
    assert user_prof["age"] == 22
    assert user_prof["district"] == "Madurai"
    print("   [OK] User profile stored in backend database.")

    # Step 4: SCHEME SEARCH ("education")
    print("\n4. SEARCHING SCHEMES FOR 'education'...")
    r = client.get("/api/v1/schemes?search=education")
    assert r.status_code == 200
    search_results = r.json()
    assert len(search_results) > 0, "No schemes returned for 'education'"
    print(f"   [OK] Search returned {len(search_results)} schemes matching 'education'.")

    # Step 5: FILTER SCHEMES (Tamil Nadu)
    print("\n5. FILTERING SCHEMES FOR STATE 'Tamil Nadu'...")
    r = client.get("/api/v1/schemes?state=Tamil%20Nadu")
    assert r.status_code == 200
    tn_results = r.json()
    assert len(tn_results) > 0
    # Verify state filtering includes Tamil Nadu + All India/Central schemes
    for s in tn_results:
        scope = (s.get("state_district_scope") or "").lower()
        assert scope in ["tamil nadu", "all india", "central", ""] or "tamil nadu" in scope or "all india" in scope or "central" in scope
    print(f"   [OK] Filter returned {len(tn_results)} schemes (Tamil Nadu + Central/All India).")

    # Step 6: OPEN SCHEME DETAILS
    target_scheme = search_results[0]
    scheme_id = target_scheme["id"]
    print(f"\n6. FETCHING SCHEME DETAILS FOR '{target_scheme['title']}' ({scheme_id})...")
    r = client.get(f"/api/v1/schemes/{scheme_id}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["title"] == target_scheme["title"]
    assert detail["official_website"] is not None or detail["source_url"] is not None
    official_url = detail["official_website"] or detail["source_url"]
    print(f"   [OK] Scheme details retrieved. Official URL: {official_url}")

    # Step 7 & 8: CHECK ELIGIBILITY WITH PROFILE
    print(f"\n7 & 8. CHECKING ELIGIBILITY FOR SCHEME '{detail['title']}' WITH PROFILE DATA...")
    eligibility_req = {
        "age": 22,
        "gender": "male",
        "annual_income": 150000.0,
        "district": "Madurai",
        "occupation": "Student",
        "disability_status": False,
        "community": "OBC",
        "marital_status": "Single"
    }
    r = client.post("/api/v1/eligibility/evaluate", json=eligibility_req, headers=headers)
    assert r.status_code == 200
    elig_result = r.json()
    assert "recommendations" in elig_result
    print(f"   [OK] Eligibility evaluated. Total evaluated schemes: {elig_result['total_schemes_evaluated']}")
    print(f"   [OK] High priority recommendations: {len(elig_result['recommendations']['high_priority'])}")

    # Step 9 & 10: SUBMIT APPLICATION FOR SCHEME
    print(f"\n9 & 10. SUBMITTING APPLICATION FOR SCHEME '{detail['title']}'...")
    app_payload = {
        "scheme_id": scheme_id
    }
    r = client.post("/api/v1/applications", json=app_payload, headers=headers)
    assert r.status_code in [200, 201], f"Application submission failed: {r.text}"
    app_record = r.json()
    app_id = app_record["id"]
    print(f"   [OK] Application created in DB. Application ID: {app_id}, Status: {app_record['status']}")

    # Step 11: FETCH USER APPLICATIONS LIST
    print("\n11. FETCHING USER APPLICATIONS LIST...")
    r = client.get("/api/v1/applications", headers=headers)
    assert r.status_code == 200
    user_apps = r.json()
    assert len(user_apps) >= 1
    assert any(a["id"] == app_id for a in user_apps)
    print(f"   [OK] User applications list contains {len(user_apps)} application(s).")

    # Step 12: DASHBOARD VERIFICATION
    print("\n12. FETCHING USER DASHBOARD STATS...")
    r = client.get("/api/v1/dashboard/stats", headers=headers)
    assert r.status_code == 200
    dash = r.json()
    assert len(dash["applications"]) >= 1
    assert dash["user_profile"]["full_name"] == "Ramesh Swaminathan"
    print(f"   [OK] Dashboard summary retrieved. User: {dash['user_profile']['full_name']}, Applications: {len(dash['applications'])}")

    # Step 13: PERSISTENCE VERIFICATION (RE-LOGIN)
    print("\n13. VERIFYING DATA PERSISTENCE ACROSS RE-LOGIN...")
    r = client.post("/api/v1/auth/login", json={"email": unique_email, "password": "Password123!"})
    assert r.status_code == 200
    mfa_tok2 = r.json()["mfa_token"]
    r = client.post(f"/api/v1/auth/mfa/verify?mfa_token={mfa_tok2}&totp_code={totp.now()}")
    assert r.status_code == 200
    new_token = r.json()["access_token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}

    # Fetch profile, applications again
    r1 = client.get("/api/v1/auth/me", headers=new_headers)
    assert r1.status_code == 200
    assert r1.json()["full_name"] == "Ramesh Swaminathan"

    r2 = client.get("/api/v1/applications", headers=new_headers)
    assert r2.status_code == 200
    assert any(a["id"] == app_id for a in r2.json())

    r3 = client.get("/api/v1/dashboard/stats", headers=new_headers)
    assert r3.status_code == 200
    assert len(r3.json()["applications"]) >= 1

    print("   [OK] All user profile, application, and dashboard stats persisted cleanly in database.")

    print("\n" + "=" * 70)
    print("COMPLETE USER JOURNEY TEST PASSED 100% SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_user_journey_test()
