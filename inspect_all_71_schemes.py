import sqlite3
import json

conn = sqlite3.connect('legal_welfare.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
schemes = [dict(r) for r in cursor.execute("SELECT * FROM schemes").fetchall()]
conn.close()

print(f"Total schemes in DB: {len(schemes)}")

cat_counts = {}
for s in schemes:
    cat = s.get("category_name") or s.get("category") or "UNKNOWN"
    cat_counts[cat] = cat_counts.get(cat, 0) + 1

print("\n--- DB CATEGORY COUNTS ---")
for cat, count in sorted(cat_counts.items()):
    print(f"{cat}: {count}")

print("\n--- SAMPLE SCHEMES PER CATEGORY ---")
for cat in sorted(cat_counts.keys()):
    cat_schemes = [s for s in schemes if (s.get("category_name") or s.get("category")) == cat]
    print(f"\nCategory: [{cat}] ({len(cat_schemes)} schemes)")
    for s in cat_schemes[:3]:
        print(f"  - Title: {s.get('title')}")
        print(f"    State/Scope: {s.get('state_district_scope')}")
        print(f"    Gender Req: {s.get('gender_restriction')}")
        print(f"    Target Occ: {s.get('target_occupation')}")
        print(f"    Target Comm: {s.get('target_community')}")
        print(f"    Elig Desc: {str(s.get('eligibility_description'))[:120]}...")
