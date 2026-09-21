import sqlite3
import json
import os
import re

db_path = "legal_welfare.db"
if not os.path.exists(db_path):
    db_path = os.path.join("backend", "legal_welfare.db")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

schemes = [dict(r) for r in cursor.execute("SELECT * FROM schemes").fetchall()]
print(f"Total schemes in DB: {len(schemes)}")

class SchemeEligibilityDeriver:
    @staticmethod
    def derive_profile(s: dict) -> dict:
        title = str(s.get("title") or "")
        title_ta = str(s.get("title_ta") or "")
        cat_name = str(s.get("category_name") or s.get("category") or "")
        legal_sum = str(s.get("legal_summary") or "")
        simple_sum = str(s.get("simple_summary") or "")
        eli10 = str(s.get("eli10_summary") or "")
        elig_desc = str(s.get("eligibility_description") or "")
        benefits = str(s.get("benefits_summary") or "")
        community = str(s.get("target_community") or "")
        occupation = str(s.get("target_occupation") or "")
        scope = str(s.get("state_district_scope") or "")
        g_req = str(s.get("gender_restriction") or "")
        min_age = s.get("min_age")
        max_age = s.get("max_age")

        full_text = f"{title} {title_ta} {cat_name} {legal_sum} {simple_sum} {eli10} {elig_desc} {benefits} {community} {occupation} {scope}".lower()

        # 1. GENDER DERIVATION
        fem_terms = ["female", "women", "woman", "girl", "daughter", "widow", "maternity", "pregnant", "mother", "magalir", "urimai", "pen", "பெண்", "பெண்கள்", "மகளிர்", "महिला", "बेटी", "स्त्री", "नारी", "गर्भवती"]
        male_terms = ["male", "men", "boy", "son", "ஆண்", "ஆண்கள்", "पुरुष", "लड़का"]
        
        has_fem = any(w in full_text for w in fem_terms) or g_req.lower() in ["female", "women"]
        has_male = any(w in full_text for w in male_terms) or g_req.lower() in ["male", "men"]

        if has_fem and not has_male:
            derived_gender = "FEMALE" # Applies to Female or All
        elif has_male and not has_fem:
            derived_gender = "MALE"
        elif g_req.lower() == "all" or (not has_fem and not has_male):
            derived_gender = "ALL"
        else:
            derived_gender = "ALL"

        # 2. CATEGORY DERIVATION
        categories = set()
        if cat_name:
            categories.add(cat_name.strip())

        cat_keywords = {
            "Education & Scholarships": ["education", "scholarship", "school", "college", "student", "samagra", "pudhumai", "study", "degree", "கல்வி", "படிப்பு", "பள்ளி", "கல்லூரி", "மாணவ", "शिक्षा", "पढ़ाई", "छात्रवृत्ति", "स्कूल"],
            "Housing & Urban Development": ["housing", "awas", "shelter", "home", "house", "building", "urban development", "வீடு", "குடியிருப்பு", "ஆவாஸ்", "घर", "मकान", "आवास", "गृह"],
            "Agriculture & Farmers Welfare": ["agriculture", "farmer", "kisan", "crop", "cultivation", "uzhavar", "விவசாயம்", "உழவர்", "பயிர்", "किसान", "कृषि", "फसल"],
            "Healthcare & Insurance": ["healthcare", "health", "insurance", "medical", "hospital", "ayushman", "maruthuvam", "சுகாதாரம்", "மருத்துவம்", "स्वास्थ्य", "अस्पताल", "बीमा", "इलाज"],
            "Social Welfare & Pensions": ["social welfare", "pension", "elderly", "old age", "welfare", "disabled", "widow", "ஓய்வூதியம்", "पेंशन", "वृद्धावस्था"],
            "Women & Child Development": ["women", "child", "girl", "maternity", "mother", "magalir", "urimai", "மகளிர்", "பெண்", "महिला", "बेटी"],
            "Employment & Skill Development": ["employment", "skill", "job", "unemployed", "work", "career", "வேலை", "தொழில்", "रोजगार", "नौकरी"],
            "Financial Inclusion & Credit": ["financial", "credit", "bank", "mudra", "loan", "dbt", "பணம்", "கடன்", "ऋण", "बैंक"],
            "Small Business & MSME": ["small business", "msme", "vendor", "svanidhi", "entrepreneur", "வியாபாரம்", "व्यापार"],
            "Rural Development": ["rural", "gramin", "panchayat", "village", "கிராமப்புற", "ग्रामीण"]
        }

        for cat, keywords in cat_keywords.items():
            if any(k in full_text for k in keywords):
                categories.add(cat)

        # 3. STATE / UT DERIVATION
        states = set()
        if "tamil nadu" in full_text or "tn" in scope.lower() or "தமிழ்நாடு" in full_text or "तमिलनाडु" in full_text:
            states.add("Tamil Nadu")
        if "urban india" in full_text or "urban" in scope.lower():
            states.add("Urban India")
        if "all india" in full_text or "central" in full_text or "national" in full_text or not scope:
            states.add("All India")

        return {
            "id": s.get("id"),
            "title": title,
            "derived_gender": derived_gender,
            "derived_categories": list(categories),
            "derived_states": list(states),
            "min_age": min_age,
            "max_age": max_age
        }

# Evaluate test cases
profiles = [SchemeEligibilityDeriver.derive_profile(s) for s in schemes]

# Test 1: Education & Scholarships
edu_schemes = [p for p in profiles if "Education & Scholarships" in p["derived_categories"]]
print(f"Education & Scholarships Count: {len(edu_schemes)}")

# Test 2: Female
female_schemes = [p for p in profiles if p["derived_gender"] in ["FEMALE", "ALL"]]
print(f"Female Eligible Schemes Count: {len(female_schemes)}")

# Test 3: Education & Scholarships + Female
edu_female = [p for p in profiles if "Education & Scholarships" in p["derived_categories"] and p["derived_gender"] in ["FEMALE", "ALL"]]
print(f"Education & Scholarships + Female Count: {len(edu_female)}")

# Test 4: Tamil Nadu + Education & Scholarships + Female
tn_edu_female = [
    p for p in profiles 
    if "Education & Scholarships" in p["derived_categories"] 
    and p["derived_gender"] in ["FEMALE", "ALL"]
    and any(st in p["derived_states"] for st in ["Tamil Nadu", "All India"])
]
print(f"Tamil Nadu + Education & Scholarships + Female Count: {len(tn_edu_female)}")

conn.close()
