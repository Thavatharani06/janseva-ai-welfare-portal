import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_all_apis():
    print("--- TESTING FASTAPI BACKEND API ENDPOINTS ---")
    
    # 1. Health Check
    r = httpx.get("http://127.0.0.1:8000/health")
    print("Health API:", r.status_code, r.json())

    # 2. Schemes API
    r = httpx.get(f"{BASE_URL}/schemes")
    print("Schemes API:", r.status_code, "Count:", len(r.json()) if r.status_code == 200 else r.text)

    # 3. Eligibility Check API
    payload = {"age": 17, "annual_income": 50000, "gender": "Female", "occupation": "Student", "district": "Madurai", "community": "SC / ST"}
    r = httpx.post(f"{BASE_URL}/eligibility/check", json=payload)
    print("Eligibility API (/eligibility/check):", r.status_code, "Keys:", list(r.json().keys()) if r.status_code == 200 else r.text)

    # 4. Voice Process API
    v_payload = {"user_id": "test_user", "raw_transcript": "My name is Suresh, Coimbatore district, mobile 9876543210, income 150000", "language": "en"}
    r = httpx.post(f"{BASE_URL}/voice/process-voice", json=v_payload)
    print("Voice API (/voice/process-voice):", r.status_code, "Response:", r.json() if r.status_code == 200 else r.text)

if __name__ == "__main__":
    test_all_apis()
