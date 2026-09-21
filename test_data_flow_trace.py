import sqlite3
from streamlit_app import fetch_schemes_from_sqlite_db, SchemeEligibilityDeriver

def test_data_flow():
    # Load all schemes directly from SQLite DB
    conn = sqlite3.connect("legal_welfare.db")
    conn.row_factory = sqlite3.Row
    db_schemes = [dict(r) for r in conn.cursor().execute("SELECT * FROM schemes").fetchall()]
    conn.close()

    print(f"1. Total schemes loaded from SQLite DB: {len(db_schemes)}")

    # Load master eligibility index
    master_index = SchemeEligibilityDeriver.get_index()
    print(f"2. Total schemes indexed in Master Eligibility Index: {len(master_index)}")

    # Check Healthcare & Insurance in Master Index
    hc_master = [s for s in db_schemes if master_index.get(s["id"], {}).get("category") == "Healthcare & Insurance"]
    print(f"3. Number of master-catalog schemes with canonical category == 'Healthcare & Insurance': {len(hc_master)}")
    print("4. Healthcare & Insurance scheme names:")
    for s in hc_master:
        print(f"   - [{s['code']}] {s['title']} (DB category_name: {s.get('category_name')})")

    # Test fetch_schemes_from_sqlite_db with category parameter
    params_cat = {"category": "Healthcare & Insurance"}
    fetched_sqlite = fetch_schemes_from_sqlite_db(params_cat)
    print(f"\n5. fetch_schemes_from_sqlite_db(category='Healthcare & Insurance') returned: {len(fetched_sqlite)} schemes")

    # Test with neutral defaults passed into API params (the bug scenario!)
    bug_params = {
        "category": "Healthcare & Insurance",
        "gender": "All",
        "community": "Select",
        "occupation": "Select",
        "residence": "Select"
    }
    fetched_bug = fetch_schemes_from_sqlite_db(bug_params)
    print(f"6. fetch_schemes_from_sqlite_db with extra params returned: {len(fetched_bug)} schemes")

if __name__ == "__main__":
    test_data_flow()
