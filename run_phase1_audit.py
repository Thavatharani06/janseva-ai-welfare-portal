import json
import sys

def main():
    audit_table = [
        {
            "field": "Aadhaar Number (Form Input)",
            "source": "Hardcoded UI string fallback ('XXXX-XXXX-8912')",
            "file": "streamlit_app.py",
            "function": "render_apply_page()",
            "db_col": "None (Not present in User DB table)",
            "real_or_demo": "DEMO PROFILE DATA"
        },
        {
            "field": "Aadhaar Document (DigiLocker)",
            "source": "DigiLocker OAuth service document sync",
            "file": "backend/app/services/digilocker_service.py",
            "function": "_sync_authorized_documents()",
            "db_col": "digilocker_documents.extracted_data",
            "real_or_demo": "REAL_DIGILOCKER (Simulated OAuth flow)"
        },
        {
            "field": "Full Name (Default Citizen)",
            "source": "Database Seed ('Arun Kumar (Demo Citizen)')",
            "file": "backend/app/services/seed_service.py",
            "function": "seed_initial_welfare_data()",
            "db_col": "users.full_name",
            "real_or_demo": "DEMO PROFILE DATA"
        },
        {
            "field": "Full Name (Application Fallback)",
            "source": "Hardcoded UI fallback ('Ramesh Swaminathan')",
            "file": "streamlit_app.py",
            "function": "render_apply_page()",
            "db_col": "None",
            "real_or_demo": "DEMO PROFILE DATA"
        },
        {
            "field": "Date of Birth / Age",
            "source": "User model (24 / 2002-08-14) or DigiLocker override",
            "file": "backend/app/models/user.py & backend/app/services/profile_service.py",
            "function": "get_normalized_profile()",
            "db_col": "users.age",
            "real_or_demo": "DEMO PROFILE DATA / REAL_DIGILOCKER"
        },
        {
            "field": "Gender",
            "source": "User model ('male') or DigiLocker override",
            "file": "backend/app/models/user.py & backend/app/services/profile_service.py",
            "function": "get_normalized_profile()",
            "db_col": "users.gender",
            "real_or_demo": "DEMO PROFILE DATA / REAL_DIGILOCKER"
        },
        {
            "field": "Residential Address",
            "source": "Hardcoded UI string fallback ('12/4, Gandhi Road, Tallakulam, Madurai')",
            "file": "streamlit_app.py",
            "function": "render_apply_page()",
            "db_col": "None",
            "real_or_demo": "DEMO PROFILE DATA"
        },
        {
            "field": "Annual Household Income",
            "source": "User model (120,000.0) or DigiLocker override (150,000.0)",
            "file": "backend/app/models/user.py & backend/app/services/profile_service.py",
            "function": "get_normalized_profile()",
            "db_col": "users.annual_income",
            "real_or_demo": "DEMO PROFILE DATA / REAL_DIGILOCKER"
        }
    ]

    print("| FIELD | VALUE SOURCE | FILE | FUNCTION/ROUTE | DATABASE COLUMN | REAL OR DEMO |")
    print("|---|---|---|---|---|---|")
    for row in audit_table:
        print(f"| {row['field']} | {row['source']} | {row['file']} | {row['function']} | {row['db_col']} | {row['real_or_demo']} |")

    print("\nCONCLUSION:")
    print("DIGILOCKER_DATA_SOURCE = DEMO_PROFILE (for form fallback defaults) / REAL_DIGILOCKER (for authorized OAuth token & document callback flow)")

if __name__ == "__main__":
    main()
