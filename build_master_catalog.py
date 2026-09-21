import sqlite3
import json
import re
import os

# 10 Canonical Categories
CANONICAL_CATEGORIES = [
    "Agriculture & Farmers Welfare",
    "Education & Scholarships",
    "Employment & Skill Development",
    "Financial Inclusion & Credit",
    "Healthcare & Insurance",
    "Housing & Urban Development",
    "Rural Development",
    "Small Business & MSME",
    "Social Welfare & Pensions",
    "Women & Child Development"
]

def normalize_category(raw_cat: str, title: str = "", desc: str = "") -> str:
    raw = (raw_cat or "").strip().lower()
    t = title.lower()
    d = desc.lower()

    if "agriculture" in raw or "farmer" in raw or "kisan" in raw or "fasal" in raw or "crop" in raw:
        return "Agriculture & Farmers Welfare"
    if "education" in raw or "scholarship" in raw or "student" in raw or "school" in raw or "shiksha" in raw:
        return "Education & Scholarships"
    if "employment" in raw or "skill" in raw or "kaushal" in raw or "job" in raw or "rozgar" in raw or "mgnrega" in raw:
        return "Employment & Skill Development"
    if "financial" in raw or "credit" in raw or "bank" in raw or "mudra" in raw or "inclusion" in raw:
        return "Financial Inclusion & Credit"
    if "health" in raw or "insurance" in raw or "medical" in raw or "bima" in raw or "ayushman" in raw or "maruthuvam" in raw:
        return "Healthcare & Insurance"
    if "housing" in raw or "urban" in raw or "awas" in raw or "green house" in raw:
        return "Housing & Urban Development"
    if "rural" in raw or "nrlm" in raw or "svamitva" in raw or "gramin" in raw:
        return "Rural Development"
    if "small business" in raw or "msme" in raw or "vendor" in raw or "vishwakarma" in raw or "business" in raw or "entrepreneur" in raw:
        return "Small Business & MSME"
    if "social welfare" in raw or "pension" in raw or "disability" in raw or "widow" in raw or "old age" in raw:
        return "Social Welfare & Pensions"
    if "women" in raw or "child" in raw or "magalir" in raw or "matru" in raw or "girl" in raw or "sukanya" in raw or "pudhumai" in raw:
        return "Women & Child Development"

    # Secondary check on title/desc if category_name is ambiguous
    comb = f"{t} {d}"
    if any(k in comb for k in ["farmer", "kisan", "crop", "agriculture"]): return "Agriculture & Farmers Welfare"
    if any(k in comb for k in ["scholarship", "student", "school", "education"]): return "Education & Scholarships"
    if any(k in comb for k in ["employment", "skill", "kaushal", "job", "work"]): return "Employment & Skill Development"
    if any(k in comb for k in ["health", "hospital", "medical", "insurance"]): return "Healthcare & Insurance"
    if any(k in comb for k in ["house", "housing", "awas"]): return "Housing & Urban Development"
    if any(k in comb for k in ["pension", "widow", "disability"]): return "Social Welfare & Pensions"
    if any(k in comb for k in ["women", "girl", "magalir", "matru"]): return "Women & Child Development"

    return "Social Welfare & Pensions"

def build_scheme_profile(s: dict) -> dict:
    title = str(s.get("title") or "")
    title_ta = str(s.get("title_ta") or "")
    title_hi = str(s.get("title_hi") or "")
    raw_cat = str(s.get("category_name") or s.get("category") or "")
    g_req = str(s.get("gender_restriction") or "")
    scope = str(s.get("state_district_scope") or "")
    occ = str(s.get("target_occupation") or "")
    comm = str(s.get("target_community") or "")
    elig = str(s.get("eligibility_description") or "")
    legal = str(s.get("legal_summary") or "")
    simple = str(s.get("simple_summary") or "")
    benefits = str(s.get("benefits_summary") or "")

    full_text = f"{g_req} {elig} {legal} {simple} {occ} {comm}".lower()
    elig_lower = f"{g_req} {elig}".lower()

    # 1. Gender Derivation
    fem_regex = r"\b(female|girl|girls|woman|women|daughter|widow|widows|maternity|pregnant|mother|magalir|urimai|pen|பெண்|பெண்கள்|மகளிர்|महिला|बेटी|स्त्री)\b"
    male_regex = r"\b(male|man|men|boy|boys|son|ஆண்|ஆண்கள்|पुरुष)\b"

    has_fem = bool(re.search(fem_regex, elig_lower)) or g_req.lower() in ["female", "women"]
    has_male = bool(re.search(male_regex, elig_lower)) or g_req.lower() in ["male", "men"]

    if has_fem and not has_male:
        gender = "FEMALE"
    elif has_male and not has_fem:
        gender = "MALE"
    elif g_req.lower() in ["all", "general", "unrestricted", "any"] or "all citizens" in full_text or "all individuals" in full_text or "all persons" in full_text or "all farmers" in full_text or "all students" in full_text:
        gender = "ALL"
    else:
        # If no explicit gender restriction specified, default to ALL for discovery
        gender = "ALL"

    # 2. Canonical Category
    category = normalize_category(raw_cat, title, f"{legal} {simple}")

    # 3. State Scope
    states = []
    scope_lower = scope.lower()
    if "tamil nadu" in scope_lower or "tn" in scope_lower or "தமிழ்நாடு" in scope_lower or "tamil nadu" in title.lower():
        states.append("Tamil Nadu")
    if "all india" in scope_lower or "central" in scope_lower or "urban india" in scope_lower or "rural india" in scope_lower or not scope_lower or "national" in scope_lower:
        states.append("All India")
    if not states:
        states.append("All India")

    # 4. Age limits
    min_age = s.get("min_age")
    max_age = s.get("max_age")
    if min_age is None or min_age == 0:
        age_min_match = re.search(r'\b(aged|age|above|minimum)\s+(\d{1,2})\b', elig_lower)
        if age_min_match:
            min_age = int(age_min_match.group(2))
    if max_age is None:
        age_max_match = re.search(r'\b(below|up to|maximum|under)\s+(\d{1,2})\b', elig_lower)
        if age_max_match:
            max_age = int(age_max_match.group(2))

    # 5. Caste / Community
    caste = "UNKNOWN"
    if comm and comm.lower() not in ["all", "none", "select", ""]:
        caste = comm
    elif "sc/st" in full_text or ("scheduled caste" in full_text and "scheduled tribe" in full_text):
        caste = "SC/ST"
    elif "scheduled caste" in full_text or r"\bsc\b" in full_text:
        caste = "SC"
    elif "scheduled tribe" in full_text or r"\bst\b" in full_text:
        caste = "ST"
    elif "obc" in full_text or "other backward" in full_text:
        caste = "OBC"
    elif "minority" in full_text or "minorities" in full_text:
        caste = "Minority"

    # 6. Student status
    is_student = "UNKNOWN"
    if "student" in occ.lower() or "student" in title.lower() or "scholarship" in title.lower() or "studying" in elig_lower or "school" in elig_lower or "college" in elig_lower:
        is_student = True

    # 7. Occupation
    occupation = "UNKNOWN"
    if occ and occ.lower() not in ["all", "none", "select", ""]:
        occupation = occ
    elif "farmer" in full_text or "kisan" in full_text:
        occupation = "Farmer"
    elif "artisan" in full_text or "vishwakarma" in full_text:
        occupation = "Artisan"
    elif "vendor" in full_text or "hawker" in full_text:
        occupation = "Street Vendor"
    elif "student" in full_text:
        occupation = "Student"
    elif "worker" in full_text or "laborer" in full_text:
        occupation = "Unorganized Worker"

    # 8. Disability
    disability_required = s.get("disability_required")
    is_disabled = "UNKNOWN"
    if disability_required == 1 or "disability" in elig_lower or "disabled" in elig_lower or "handicapped" in elig_lower:
        is_disabled = True

    # 9. Marital Status
    marital = "UNKNOWN"
    if "widow" in elig_lower or "widows" in elig_lower:
        marital = "Widow"
    elif "unmarried" in elig_lower or "single girl" in elig_lower:
        marital = "Single"

    # 10. Residence
    residence = "ALL"
    if "rural" in scope_lower or "rural" in elig_lower:
        residence = "Rural"
    elif "urban" in scope_lower or "urban" in elig_lower:
        residence = "Urban"

    return {
        "id": s.get("id"),
        "code": s.get("code"),
        "title": title,
        "title_ta": title_ta,
        "title_hi": title_hi,
        "category": category,
        "gender": gender,
        "states": states,
        "min_age": min_age if min_age is not None else "UNKNOWN",
        "max_age": max_age if max_age is not None else "UNKNOWN",
        "caste": caste,
        "residence": residence,
        "student": is_student,
        "occupation": occupation,
        "disability": is_disabled,
        "marital": marital,
        "eligibility_description": elig,
        "benefits_summary": benefits,
        "official_url": s.get("official_website") or s.get("source_url") or ""
    }

def main():
    conn = sqlite3.connect("legal_welfare.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    schemes = [dict(r) for r in cursor.execute("SELECT * FROM schemes").fetchall()]
    conn.close()

    master_catalog = {}
    cat_tree = {c: [] for c in CANONICAL_CATEGORIES}

    for s in schemes:
        prof = build_scheme_profile(s)
        sid = s.get("id")
        master_catalog[sid] = prof
        cat_tree[prof["category"]].append(prof)

    print(f"==================================================")
    print(f"MASTER 71-SCHEME ELIGIBILITY CATALOG GENERATED")
    print(f"Total schemes indexed: {len(master_catalog)}")
    print(f"==================================================\n")

    print("\n--- CANONICAL CATEGORY BREAKDOWN ---")
    for cat, list_s in cat_tree.items():
        print(f"\n[CATEGORY] {cat} ({len(list_s)} schemes)")
        for p in list_s:
            print(f"   |-- {p['title']} [Gender: {p['gender']} | State: {', '.join(p['states'])} | Student: {p['student']}]")

    # Save to json file for persistence
    with open("master_eligibility_index.json", "w", encoding="utf-8") as f:
        json.dump(master_catalog, f, indent=2, ensure_ascii=False)
    print("\nSaved persisted master index to master_eligibility_index.json")

if __name__ == "__main__":
    main()
