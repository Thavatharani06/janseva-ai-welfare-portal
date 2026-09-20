import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import time
import pyotp
import json
from fastapi.testclient import TestClient
from app.main import app

def run_verification_suite():
    print("=" * 60)
    print("JANSEVA AI SECURITY & JOURNEY VERIFICATION SUITE")
    print("=" * 60)

    client = TestClient(app)

    unique_email = f"test_citizen_{int(time.time())}@janseva.gov.in"

    # 1. TEST REGISTRATION & MFA SETUP
    print(f"\n[TEST 1] Registering New Citizen User ({unique_email}) & Requesting TOTP MFA Setup...")
    reg_payload = {
        "email": unique_email,
        "password": "Password123!",
        "full_name": "Arun Kumar Test Citizen",
        "language_preference": "ta"
    }
    r = client.post("/api/v1/auth/register", json=reg_payload)
    assert r.status_code == 200, f"Registration failed: {r.text}"
    mfa_setup_data = r.json()
    assert "temp_token" in mfa_setup_data
    assert "secret" in mfa_setup_data
    assert "qr_code_url" in mfa_setup_data
    assert len(mfa_setup_data["recovery_codes"]) == 8
    print("  SUCCESS: MFA QR payload, secret, and 8 recovery codes generated.")

    # 2. TEST TOTP SETUP CONFIRMATION
    print("\n[TEST 2] Confirming MFA Setup with Generated TOTP Code...")
    totp = pyotp.TOTP(mfa_setup_data["secret"])
    valid_code = totp.now()
    
    confirm_payload = {
        "temp_token": mfa_setup_data["temp_token"],
        "totp_code": valid_code
    }
    r = client.post("/api/v1/auth/mfa/confirm-setup", json=confirm_payload)
    assert r.status_code == 200, f"MFA setup confirmation failed: {r.text}"
    user_token_data = r.json()
    access_token = user_token_data["access_token"]
    print("  SUCCESS: Account activated with MFA. Received JWT Access Token.")

    # 3. TEST UNAUTHENTICATED BLOCK (NO ANONYMOUS ACCESS)
    print("\n[TEST 3] Testing Unauthenticated Access Block...")
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401, f"Expected 401 Unauthorized, got {r.status_code}"
    print("  SUCCESS: Backend correctly rejected unauthenticated request with HTTP 401.")

    # 4. TEST RETURNING USER SIGN IN & MFA CHALLENGE
    print("\n[TEST 4] Testing Returning User Sign In & TOTP Challenge...")
    login_payload = {
        "email": unique_email,
        "password": "Password123!"
    }
    r = client.post("/api/v1/auth/login", json=login_payload)
    assert r.status_code == 200
    login_mfa_data = r.json()
    assert login_mfa_data["mfa_required"] is True
    mfa_token = login_mfa_data["mfa_token"]
    print("  SUCCESS: Password verified. System issued short-lived MFA challenge token.")

    # 5. TEST INVALID TOTP CODE REJECTION
    print("\n[TEST 5] Testing Invalid TOTP Code Rejection...")
    r = client.post(f"/api/v1/auth/mfa/verify?mfa_token={mfa_token}&totp_code=000000")
    assert r.status_code == 400
    print("  SUCCESS: Invalid TOTP code correctly rejected with HTTP 400.")

    # 6. TEST VALID TOTP LOGIN VERIFICATION
    print("\n[TEST 6] Testing Valid TOTP Code Verification...")
    valid_code_2 = totp.now()
    r = client.post(f"/api/v1/auth/mfa/verify?mfa_token={mfa_token}&totp_code={valid_code_2}")
    assert r.status_code == 200
    print("  SUCCESS: Returning user authenticated successfully with TOTP MFA.")

    # 7. TEST IDOR & ADMIN ROUTE AUTHORIZATION BLOCK
    print("\n[TEST 7] Testing Role-Based Admin Route Protection...")
    headers = {"Authorization": f"Bearer {access_token}"}
    r = client.get("/api/v1/admin/analytics", headers=headers)
    assert r.status_code == 403, f"Expected 403 Forbidden for citizen, got {r.status_code}"
    print("  SUCCESS: Backend prevented citizen account from accessing admin analytics.")

    r = client.post("/api/v1/admin/trigger-myscheme-sync", headers=headers)
    assert r.status_code == 403, f"Expected 403 Forbidden for citizen, got {r.status_code}"
    print("  SUCCESS: Backend prevented citizen account from triggering myScheme sync.")

    print("\n" + "=" * 60)
    print("ALL SECURITY & AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification_suite()
