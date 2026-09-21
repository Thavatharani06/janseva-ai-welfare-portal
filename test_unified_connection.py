import sqlite3
from streamlit_app import SchemeEligibilityDeriver, normalize_canonical_category

def test_categories():
    conn = sqlite3.connect("legal_welfare.db")
    conn.row_factory = sqlite3.Row
    all_schemes = [dict(r) for r in conn.cursor().execute("SELECT * FROM schemes").fetchall()]
    conn.close()

    master_index = SchemeEligibilityDeriver.get_index()

    test_categories = [
        ("Education & Scholarships", 12),
        ("Employment & Skill Development", 8),
        ("Agriculture & Farmers Welfare", 9),
        ("Healthcare & Insurance", 8),
        ("Housing & Urban Development", 3),
        ("Social Welfare & Pensions", 10),
        ("Women & Child Development", 14),
        ("Financial Inclusion & Credit", 1),
        ("Rural Development", 2),
        ("Small Business & MSME", 4)
    ]

    print("=== TESTING UNIFIED MASTER CATALOG DISCOVERY ===")
    total_matched_sum = 0
    for cat_name, expected_count in test_categories:
        active_filters = {"category": cat_name}
        matches = []
        for s in all_schemes:
            is_match, _ = SchemeEligibilityDeriver.evaluate_scheme(s, active_filters)
            if is_match:
                matches.append(s)
        print(f"Category: [{cat_name}] -> Matched: {len(matches)} (Expected: {expected_count}) {'PASS' if len(matches) == expected_count else 'FAIL'}")
        total_matched_sum += len(matches)

    print(f"\nTotal sum of category counts: {total_matched_sum} / {len(all_schemes)}")

if __name__ == "__main__":
    test_categories()
