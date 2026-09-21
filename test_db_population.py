import sqlite3
import os
import json

base_dir = "."
db_paths = [
    os.path.join(base_dir, "legal_welfare.db"),
    os.path.join(base_dir, "backend", "legal_welfare.db")
]

for dbp in db_paths:
    print(f"\nChecking DB file: {dbp} (Exists: {os.path.exists(dbp)})")
    if os.path.exists(dbp):
        conn = sqlite3.connect(dbp)
        c = conn.cursor()
        count = c.execute("SELECT COUNT(*) FROM schemes").fetchone()[0]
        print(f" Total schemes count: {count}")
        
        # Check categories
        cats = c.execute("SELECT DISTINCT category_name FROM schemes").fetchall()
        print(" Distinct category_name:", [cat[0] for cat in cats])

        # Check PMAY-U
        pmay = c.execute("SELECT code, title, category_name, state_district_scope FROM schemes WHERE code LIKE '%PMAY%' OR title LIKE '%PMAY%'").fetchall()
        print(" PMAY rows:", pmay)
        
        # Test query for Tamil Nadu + Housing & Urban Development
        q = """
        SELECT code, title, category_name, state_district_scope 
        FROM schemes 
        WHERE (state_district_scope LIKE '%Tamil Nadu%' OR state_district_scope LIKE '%All India%' OR state_district_scope LIKE '%Central%' OR state_district_scope IS NULL)
        AND (category_name LIKE '%Housing & Urban Development%' OR category LIKE '%Housing & Urban Development%')
        """
        res = c.execute(q).fetchall()
        print(f" Query result for Tamil Nadu + Housing & Urban Development: {len(res)} schemes")
        for r in res:
            print("  ", r)
        conn.close()
