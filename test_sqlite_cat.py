import sys
import os
import sqlite3

from streamlit_app import fetch_schemes_from_sqlite_db, get_db_categories

params1 = {"state": "Tamil Nadu"}
res1 = fetch_schemes_from_sqlite_db(params1)
print("fetch_schemes_from_sqlite_db(state=Tamil Nadu) count:", len(res1))

params2 = {"state": "Tamil Nadu", "category": "Housing & Urban Development"}
res2 = fetch_schemes_from_sqlite_db(params2)
print("fetch_schemes_from_sqlite_db(state=Tamil Nadu, category=Housing & Urban Development) count:", len(res2))
for r in res2:
    print("  SQLite matched:", r.get("code"), r.get("title"))

print("\n--- Categories from get_db_categories ---")
cats = get_db_categories()
print("get_db_categories():", cats)
