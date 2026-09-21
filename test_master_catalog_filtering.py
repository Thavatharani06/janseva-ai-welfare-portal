import sqlite3
import json
from build_master_catalog import build_scheme_profile, CANONICAL_CATEGORIES

class MasterEligibilityEngine:
    _index = None

    @classmethod
    def get_index(cls):
        if cls._index is not None:
            return cls._index
        conn = sqlite3.connect("legal_welfare.db")
        conn.row_factory = sqlite3.Row
        schemes = [dict(r) for r in conn.cursor().execute("SELECT * FROM schemes").fetchall()]
        conn.close()
        cls._index = {s["id"]: build_scheme_profile(s) for s in schemes}
        return cls._index

    @classmethod
    def filter_schemes(cls, schemes, filters):
        idx = cls.get_index()
        results = []
        for s in schemes:
            sid = s.get("id")
            prof = idx.get(sid) or build_scheme_profile(s)

            # 1. Category Filter
            req_cat = filters.get("category")
            if req_cat:
                if prof["category"].lower() != req_cat.lower():
                    continue

            # 2. Gender Filter
            req_gender = filters.get("gender")
            if req_gender:
                g_clean = req_gender.strip().upper()
                if g_clean in ["FEMALE", "WOMEN"]:
                    if prof["gender"] == "MALE":
                        continue
                elif g_clean in ["MALE", "MEN"]:
                    if prof["gender"] == "FEMALE":
                        continue

            # 3. State Filter
            req_state = filters.get("state")
            if req_state:
                if req_state == "Tamil Nadu":
                    if "Tamil Nadu" not in prof["states"] and "All India" not in prof["states"]:
                        continue
                elif req_state == "All India":
                    if "All India" not in prof["states"]:
                        continue

            results.append(s)
        return results

def main():
    conn = sqlite3.connect("legal_welfare.db")
    conn.row_factory = sqlite3.Row
    all_schemes = [dict(r) for r in conn.cursor().execute("SELECT * FROM schemes").fetchall()]
    conn.close()

    print(f"Total schemes in DB: {len(all_schemes)}")

    # Test 1: No filters -> 71
    t1 = MasterEligibilityEngine.filter_schemes(all_schemes, {})
    print(f"Test 1 (No filters): {len(t1)} (Expected: 71)")

    # Test 2: Education & Scholarships
    t2 = MasterEligibilityEngine.filter_schemes(all_schemes, {"category": "Education & Scholarships"})
    print(f"Test 2 (Education & Scholarships): {len(t2)} (Expected > 0)")

    # Test 3: Employment & Skill Development
    t3 = MasterEligibilityEngine.filter_schemes(all_schemes, {"category": "Employment & Skill Development"})
    print(f"Test 3 (Employment & Skill Development): {len(t3)} (Expected > 0)")

    # Test 4: Female
    t4 = MasterEligibilityEngine.filter_schemes(all_schemes, {"gender": "Female"})
    print(f"Test 4 (Female): {len(t4)} (Expected subset < 71)")

    # Test 5: Male
    t5 = MasterEligibilityEngine.filter_schemes(all_schemes, {"gender": "Male"})
    print(f"Test 5 (Male): {len(t5)} (Expected subset < 71)")

    # Test 6: Education + Female
    t6 = MasterEligibilityEngine.filter_schemes(all_schemes, {"category": "Education & Scholarships", "gender": "Female"})
    print(f"Test 6 (Education + Female): {len(t6)}")

    # Test 7: Tamil Nadu + Education + Female
    t7 = MasterEligibilityEngine.filter_schemes(all_schemes, {"state": "Tamil Nadu", "category": "Education & Scholarships", "gender": "Female"})
    print(f"Test 7 (Tamil Nadu + Education + Female): {len(t7)}")

    # Test 8: Employment & Skill Development + Female
    t8 = MasterEligibilityEngine.filter_schemes(all_schemes, {"category": "Employment & Skill Development", "gender": "Female"})
    print(f"Test 8 (Employment & Skill Development + Female): {len(t8)}")

    # Test 9: Pudhumai Penn Check
    pudhumai = [s for s in all_schemes if "pudhumai" in s["title"].lower()][0]
    p_female = MasterEligibilityEngine.filter_schemes([pudhumai], {"gender": "Female"})
    p_male = MasterEligibilityEngine.filter_schemes([pudhumai], {"gender": "Male"})
    print(f"Pudhumai Penn in Female filter: {len(p_female) == 1} | Pudhumai Penn in Male filter: {len(p_male) == 1} (Expected: False)")

if __name__ == "__main__":
    main()
