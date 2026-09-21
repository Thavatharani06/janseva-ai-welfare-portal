import httpx
import json

def test_api_endpoint():
    api_url = "http://127.0.0.1:8000/api/v1"
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{api_url}/schemes", params={"category": "Healthcare & Insurance"})
            print(f"API Response Status Code: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"API returned {len(data)} schemes for category 'Healthcare & Insurance'")
                for d in data:
                    print(f" - {d.get('title')}")
            else:
                print(f"API Error Response: {resp.text}")
    except Exception as e:
        print(f"Could not connect to FastAPI server at {api_url}: {e}")

if __name__ == "__main__":
    test_api_endpoint()
