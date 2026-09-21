import sqlite3
import json

conn = sqlite3.connect('legal_welfare.db')
c = conn.cursor()

tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
print("Tables in legal_welfare.db:", tables)

print("\n--- PMAY / Housing Schemes in schemes table ---")
rows = c.execute("SELECT id, code, title, category_name, category, category_id FROM schemes WHERE title LIKE '%PMAY%' OR code LIKE '%PMAY%' OR title LIKE '%Awas%' OR category_name LIKE '%Housing%' OR category LIKE '%Housing%'").fetchall()
for r in rows:
    print(r)

print("\n--- Distinct category_name values in schemes table ---")
cats_name = c.execute("SELECT DISTINCT category_name FROM schemes").fetchall()
for cat in cats_name:
    print("category_name:", repr(cat[0]))

print("\n--- Distinct category values in schemes table ---")
cats_cat = c.execute("SELECT DISTINCT category FROM schemes").fetchall()
for cat in cats_cat:
    print("category:", repr(cat[0]))

if "scheme_categories" in tables:
    print("\n--- Table: scheme_categories ---")
    sc_rows = c.execute("SELECT * FROM scheme_categories").fetchall()
    for sc in sc_rows:
        print(sc)

conn.close()
