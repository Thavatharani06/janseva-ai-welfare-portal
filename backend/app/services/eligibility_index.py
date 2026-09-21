import sqlite3
import json
import os
import re
from typing import Dict, Any, List, Optional

class StructuredEligibilityIndex:
    """
    Persisted & Cached Structured Eligibility Index for all 71 schemes.
    Derives positive eligibility facts from actual eligibility_description, 
    gender_restriction, target_community, target_occupation, state_district_scope, 
    and category_name.
    """
    _cached_index: Optional[Dict[str, Dict[str, Any]]] = None

    @classmethod
    def get_index(cls, db_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        if cls._cached_index is not None:
            return cls._cached_index

        if not db_path or not os.path.exists(db_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "legal_welfare.db")
            if not os.path.exists(db_path):
                db_path = os.path.join(base_dir, "backend", "legal_welfare.db")

        if not os.path.exists(db_path):
            return {}

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        schemes = [dict(r) for r in cursor.execute("SELECT * FROM schemes").fetchall()]
        conn.close()

        cls._cached_index = {s["id"]: cls.build_profile(s) for s in schemes}
        return cls._cached_index

    @classmethod
    def build_profile(cls, s: Dict[str, Any]) -> Dict[str, Any]:
        title = str(s.get("title") or "")
        title_ta = str(s.get("title_ta") or "")
        cat_name = str(s.get("category_name") or s.get("category") or "")
        g_req = str(s.get("gender_restriction") or "")
        scope = str(s.get("state_district_scope") or "")
        occ = str(s.get("target_occupation") or "")
        comm = str(s.get("target_community") or "")
        elig = str(s.get("eligibility_description") or "")
        benefits = str(s.get("benefits_summary") or "")

        elig_text = f"{g_req} {elig}".lower()

        # 1. GENDER DERIVATION (Exact Word Boundary Regex)
        fem_regex = r"\b(female|girl|girls|woman|women|daughter|widow|widows|maternity|pregnant|mother|magalir|urimai|pen|பெண்|பெண்கள்|மகளிர்|महिला|बेटी|स्त्री)\b"
        male_regex = r"\b(male|man|men|boy|boys|son|ஆண்|ஆண்கள்|पुरुष)\b"

        has_fem = bool(re.search(fem_regex, elig_text)) or g_req.lower() in ["female", "women"]
        has_male = bool(re.search(male_regex, elig_text)) or g_req.lower() in ["male", "men"]

        if has_fem and not has_male:
            gender = "FEMALE"
        elif has_male and not has_fem:
            gender = "MALE"
        else:
            gender = "ALL"

        # 2. CANONICAL CATEGORY DERIVATION
        cat_map = {
            "education": "Education & Scholarships",
            "scholarship": "Education & Scholarships",
            "housing": "Housing & Urban Development",
            "urban": "Housing & Urban Development",
            "agriculture": "Agriculture & Farmers Welfare",
            "farmer": "Agriculture & Farmers Welfare",
            "health": "Healthcare & Insurance",
            "insurance": "Healthcare & Insurance",
            "social": "Social Welfare & Pensions",
            "pension": "Social Welfare & Pensions",
            "women": "Women & Child Development",
            "child": "Women & Child Development",
            "employment": "Employment & Skill Development",
            "skill": "Employment & Skill Development",
            "financial": "Financial Inclusion & Credit",
            "credit": "Financial Inclusion & Credit",
            "business": "Small Business & MSME",
            "msme": "Small Business & MSME",
            "rural": "Rural Development"
        }
        canonical_cat = "General Welfare"
        c_lower = cat_name.lower()
        for k, v in cat_map.items():
            if k in c_lower:
                canonical_cat = v
                break

        # 3. STATE SCOPE
        states = set()
        s_lower = scope.lower()
        if "tamil nadu" in s_lower or "tn" in s_lower or "தமிழ்நாடு" in s_lower:
            states.add("Tamil Nadu")
        if "all india" in s_lower or "central" in s_lower or not s_lower:
            states.add("All India")
        if not states:
            states.add("All India")

        # 4. OCCUPATION
        occupations = set()
        full_elig = f"{occ} {elig}".lower()
        if "student" in full_elig or "scholar" in full_elig or "school" in full_elig or "college" in full_elig or "மாணவ" in full_elig or "छात्र" in full_elig:
            occupations.add("Student")
        if "farmer" in full_elig or "kisan" in full_elig or "cultivator" in full_elig or "uzhavar" in full_elig or "விவசாயி" in full_elig or "किसान" in full_elig:
            occupations.add("Farmer")
        if "unorganized" in full_elig or "vendor" in full_elig or "artisan" in full_elig or "worker" in full_elig or "தொழிலாளி" in full_elig or "मज़दूर" in full_elig:
            occupations.add("Unorganized Worker")
        if "homemaker" in full_elig or "housewife" in full_elig or "गृहणी" in full_elig:
            occupations.add("Homemaker")
        if not occupations:
            occupations.add("ALL")

        return {
            "id": s.get("id"),
            "code": s.get("code"),
            "title": title,
            "title_ta": title_ta,
            "gender": gender,
            "category": canonical_cat,
            "states": list(states),
            "occupations": list(occupations),
            "min_age": s.get("min_age"),
            "max_age": s.get("max_age"),
            "disability_required": bool(s.get("disability_required"))
        }

    @classmethod
    def evaluate_scheme(cls, s: Dict[str, Any], active_filters: Dict[str, Any], db_path: Optional[str] = None) -> bool:
        idx = cls.get_index(db_path)
        sid = s.get("id")
        profile = idx.get(sid) or cls.build_profile(s)

        # 1. State / UT Filter
        req_state = active_filters.get("state")
        if req_state:
            if req_state == "Tamil Nadu":
                if "Tamil Nadu" not in profile["states"] and "All India" not in profile["states"]:
                    return False
            elif req_state == "Urban India":
                if "Urban India" not in profile["states"] and "All India" not in profile["states"]:
                    return False
            elif req_state == "All India":
                if "All India" not in profile["states"]:
                    return False

        # 2. Category Filter
        req_cat = active_filters.get("category")
        if req_cat:
            if profile["category"].lower() != req_cat.lower() and req_cat.lower() not in profile["category"].lower():
                return False

        # 3. Gender Filter
        req_gender = active_filters.get("gender")
        if req_gender:
            g_clean = req_gender.strip().upper()
            if g_clean in ["FEMALE", "WOMEN"]:
                if profile["gender"] == "MALE":
                    return False
            elif g_clean in ["MALE", "MEN"]:
                if profile["gender"] == "FEMALE":
                    return False

        # 4. Age Filter
        req_age = active_filters.get("age")
        if req_age:
            min_a, max_a = None, None
            if "18" in req_age and "25" in req_age:
                min_a, max_a = 18, 25
            elif "26" in req_age and "40" in req_age:
                min_a, max_a = 26, 40
            elif "41" in req_age and "60" in req_age:
                min_a, max_a = 41, 60
            elif "60+" in req_age:
                min_a, max_a = 60, 120

            if min_a is not None and max_a is not None:
                s_min = profile.get("min_age")
                s_max = profile.get("max_age")
                if s_min is not None and s_min > max_a:
                    return False
                if s_max is not None and s_max < min_a:
                    return False

        return True
