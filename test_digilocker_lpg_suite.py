import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import time
import pyotp
import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def run_integration_suite():
    print("=" * 75)
    print("JANSEVA AI - DIGILOCKER, LPG, PROFILE & SECURITY TEST SUITE")
    print("=" * 75)

    client = TestClient(app)

    # 1. USER REGISTRATION & AUTHENTICATION
    unique_email = f"citizen_setu_{int(time.time())}@janseva.gov.in"
    print(f"\n[TEST 1] Registering & Authenticating User ({unique_email})...")
    r = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "Password123!",
        "full_name": "Ramesh Swaminathan",
        "language_preference": "ta"
    })
    assert r.status_code == 200
    reg_data = r.json()
    totp = pyotp.TOTP(reg_data["secret"])

    r = client.post("/api/v1/auth/mfa/confirm-setup", json={
        "temp_token": reg_data["temp_token"],
        "totp_code": totp.now()
    })
    assert r.status_code == 200
    access_token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("  [OK] User registered and authenticated with TOTP MFA.")

    # 2. DIGILOCKER OAUTH CONNECT URL & STATE GENERATION
    print("\n[TEST 2] Testing DigiLocker Connect URL & OAuth State Generation...")
    r = client.get("/api/v1/digilocker/connect-url", headers=headers)
    assert r.status_code == 200
    conn_url_data = r.json()
    assert "state" in conn_url_data
    assert "authorization_url" in conn_url_data
    print("  [OK] DigiLocker OAuth URL & State token generated successfully.")

    # 3. DIGILOCKER OAUTH CALLBACK & TOKEN STORAGE
    print("\n[TEST 3] Testing DigiLocker OAuth Callback & Token Encryption...")
    r = client.post("/api/v1/digilocker/callback", json={
        "code": "sample_oauth_code_98765",
        "state": conn_url_data["state"]
    }, headers=headers)
    assert r.status_code == 200
    cb_data = r.json()
    assert cb_data["status"] == "SUCCESS"
    print("  [OK] OAuth callback processed. Token stored securely.")

    # 4. DIGILOCKER STATUS & DOCUMENT RETRIEVAL
    print("\n[TEST 4] Testing DigiLocker Connection Status & Document Retrieval...")
    r = client.get("/api/v1/digilocker/status", headers=headers)
    assert r.status_code == 200
    status_data = r.json()
    assert status_data["is_connected"] is True
    assert status_data["verified_documents_count"] >= 3
    doc_types = [d["doc_type"] for d in status_data["documents"]]
    assert "AADHAAR" in doc_types
    assert "INCOME_CERTIFICATE" in doc_types
    print(f"  [OK] DigiLocker connected. Retrived {status_data['verified_documents_count']} verified documents: {doc_types}")

    # 5. LPG CONSUMER BINDING & MASKING
    print("\n[TEST 5] Testing LPG Consumer Binding & Masking Security...")
    r = client.post("/api/v1/lpg/bind", json={
        "consumer_id": "7501928374",
        "provider": "IOCL (Indane)"
    }, headers=headers)
    assert r.status_code == 200
    lpg_bind_data = r.json()
    assert lpg_bind_data["status"] == "SUCCESS"
    assert lpg_bind_data["consumer_id_masked"] == "XXXX-XXXX-8374"
    print(f"  [OK] LPG Consumer ID bound and masked securely as '{lpg_bind_data['consumer_id_masked']}'.")

    # 6. LPG SUBSIDY STATUS RETRIEVAL
    print("\n[TEST 6] Testing LPG Refill & PAHAL Subsidy Status Retrieval...")
    r = client.get("/api/v1/lpg/status", headers=headers)
    assert r.status_code == 200
    lpg_status_data = r.json()
    assert lpg_status_data["is_connected"] is True
    assert lpg_status_data["subsidy_eligible"] is True
    assert lpg_status_data["subsidy_received_amount"] == 300.0
    print(f"  [OK] Refill history & DBTL subsidy of Rs.{lpg_status_data['subsidy_received_amount']} verified.")


    # 7. NORMALIZED PROFILE & DATA PROVENANCE
    print("\n[TEST 7] Testing Normalized Citizen Profile & Data Provenance Tags...")
    r = client.get("/api/v1/profile/me", headers=headers)
    assert r.status_code == 200
    prof_data = r.json()
    assert "personal_info" in prof_data
    assert prof_data["personal_info"]["full_name"]["source"] == "DIGILOCKER"
    assert prof_data["personal_info"]["annual_income"]["source"] == "DIGILOCKER"
    assert prof_data["lpg"]["source"] == "LPG_OFFICIAL_API"
    print("  [OK] Profile data normalized with transparent provenance tags ([DIGILOCKER], [LPG_OFFICIAL_API]).")

    # 8. FAMILY MEMBER MANAGEMENT
    print("\n[TEST 8] Testing Family Information Management...")
    r = client.post("/api/v1/profile/family", json={
        "full_name": "Priya Swaminathan",
        "relationship_type": "sibling",
        "age": 19,
        "occupation": "College Student",
        "is_dependent": True
    }, headers=headers)
    assert r.status_code == 200
    fam_member = r.json()
    assert fam_member["full_name"] == "Priya Swaminathan"

    # Verify family list
    r = client.get("/api/v1/profile/me", headers=headers)
    assert len(r.json()["family_members"]) >= 1
    print("  [OK] Family member added and retrieved in household profile.")

    # 9. CROSS-USER ISOLATION AUDIT
    print("\n[TEST 9] Testing Cross-User Security Isolation...")
    other_email = f"other_citizen_{int(time.time())}@janseva.gov.in"
    r2 = client.post("/api/v1/auth/register", json={
        "email": other_email,
        "password": "Password123!",
        "full_name": "Kavitha Devi",
        "language_preference": "ta"
    })
    totp2 = pyotp.TOTP(r2.json()["secret"])
    r2_token = client.post("/api/v1/auth/mfa/confirm-setup", json={
        "temp_token": r2.json()["temp_token"],
        "totp_code": totp2.now()
    }).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {r2_token}"}

    # Verify User 2 cannot access User 1's DigiLocker or Family records
    r_digi2 = client.get("/api/v1/digilocker/status", headers=headers2)
    assert r_digi2.json()["is_connected"] is False

    r_lpg2 = client.get("/api/v1/lpg/status", headers=headers2)
    assert r_lpg2.json()["is_connected"] is False

    r_fam_del = client.delete(f"/api/v1/profile/family/{fam_member['id']}", headers=headers2)
    assert r_fam_del.status_code in [403, 404]
    print("  [OK] Cross-user data isolation verified. User 2 blocked from accessing User 1 records.")

    # 10. DISCONNECT FLOWS
    print("\n[TEST 10] Testing Disconnect Flows...")
    r = client.post("/api/v1/digilocker/disconnect", headers=headers)
    assert r.status_code == 200
    assert client.get("/api/v1/digilocker/status", headers=headers).json()["is_connected"] is False

    r = client.post("/api/v1/lpg/disconnect", headers=headers)
    assert r.status_code == 200
    assert client.get("/api/v1/lpg/status", headers=headers).json()["is_connected"] is False
    print("  [OK] DigiLocker & LPG disconnected cleanly.")

    print("\n" + "=" * 75)
    print("ALL DIGILOCKER, LPG, PROFILE & SECURITY TESTS PASSED 100% SUCCESSFULLY!")
    print("=" * 75)

if __name__ == "__main__":
    run_integration_suite()
