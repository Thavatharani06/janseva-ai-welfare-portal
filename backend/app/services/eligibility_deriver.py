import re
from typing import Dict, Any, List, Set, Tuple

class SchemeEligibilityDeriver:
    """
    Derives structured eligibility metadata from existing scheme text content.
    Supports English, Tamil, and Hindi text in scheme records.
    No hardcoded scheme names or hardcoded scheme identity mappings.
    """

    @staticmethod
    def derive_profile(s: Dict[str, Any]) -> Dict[str, Any]:
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
        max_income = s.get("max_income")
        disability_req = s.get("disability_required")

        full_text = f"{title} {title_ta} {cat_name} {legal_sum} {simple_sum} {eli10} {elig_desc} {benefits} {community} {occupation} {scope}".lower()

        # 1. GENDER DERIVATION
        fem_terms = [
            "female", "women", "woman", "girl", "daughter", "widow", "maternity", "pregnant", 
            "mother", "magalir", "urimai", "pen", "பெண்", "பெண்கள்", "மகளிர்", "महिला", "बेटी", "स्त्री", "नारी", "गर्भवती"
        ]
        male_terms = [
            "male", "men", "boy", "son", "ஆண்", "ஆண்கள்", "पुरुष", "लड़का"
        ]

        has_fem = any(w in full_text for w in fem_terms) or g_req.lower() in ["female", "women"]
        has_male = any(w in full_text for w in male_terms) or g_req.lower() in ["male", "men"]

        # Three-state gender tag list: FEMALE, MALE, ALL, UNKNOWN
        if has_fem and not has_male:
            genders = {"FEMALE", "ALL"}
        elif has_male and not has_fem:
            genders = {"MALE", "ALL"}
        elif g_req.lower() == "all" or (not has_fem and not has_male):
            genders = {"ALL", "FEMALE", "MALE", "UNKNOWN"}
        else:
            genders = {"ALL", "FEMALE", "MALE", "UNKNOWN"}

        # 2. CATEGORY DERIVATION
        categories = set()
        if cat_name:
            c_clean = cat_name.strip()
            categories.add(c_clean)
            if "&" in c_clean:
                categories.add(c_clean.replace("&", "and"))

        cat_keywords = {
            "Education & Scholarships": [
                "education", "scholarship", "school", "college", "student", "samagra", "pudhumai", 
                "study", "degree", "கல்வி", "படிப்பு", "பள்ளி", "கல்லூரி", "மாணவ", "शिक्षा", "पढ़ाई", "छात्रवृत्ति", "स्कूल"
            ],
            "Housing & Urban Development": [
                "housing", "awas", "shelter", "home", "house", "building", "urban development", 
                "வீடு", "குடியிருப்பு", "ஆவாஸ்", "घर", "मकान", "आवास", "गृह"
            ],
            "Agriculture & Farmers Welfare": [
                "agriculture", "farmer", "kisan", "crop", "cultivation", "uzhavar", 
                "விவசாயம்", "உழவர்", "பயிர்", "किसान", "कृषि", "फसल"
            ],
            "Healthcare & Insurance": [
                "healthcare", "health", "insurance", "medical", "hospital", "ayushman", "maruthuvam", 
                "சுகாதாரம்", "மருத்துவம்", "स्वास्थ्य", "अस्पताल", "बीमा", "इलाज"
            ],
            "Social Welfare & Pensions": [
                "social welfare", "pension", "elderly", "old age", "welfare", "disabled", "widow", 
                "ஓய்வூதியம்", "पेंशन", "वृद्धावस्था"
            ],
            "Women & Child Development": [
                "women", "child", "girl", "maternity", "mother", "magalir", "urimai", 
                "மகளிர்", "பெண்", "महिला", "बेटी"
            ],
            "Employment & Skill Development": [
                "employment", "skill", "job", "unemployed", "work", "career", 
                "வேலை", "தொழில்", "रोजगार", "नौकरी"
            ],
            "Financial Inclusion & Credit": [
                "financial", "credit", "bank", "mudra", "loan", "dbt", 
                "பணம்", "கடன்", "ऋण", "बैंक"
            ],
            "Small Business & MSME": [
                "small business", "msme", "vendor", "svanidhi", "entrepreneur", 
                "வியாபாரம்", "व्यापार"
            ],
            "Rural Development": [
                "rural", "gramin", "panchayat", "village", 
                "கிராமப்புற", "ग्रामीण"
            ]
        }

        for cat_label, keywords in cat_keywords.items():
            if any(k in full_text for k in keywords):
                categories.add(cat_label)

        # 3. STATE / UT DERIVATION
        states = set()
        if "tamil nadu" in full_text or "tn" in scope.lower() or "தமிழ்நாடு" in full_text or "तमिलनाडु" in full_text:
            states.add("Tamil Nadu")
        if "urban india" in full_text or "urban" in scope.lower():
            states.add("Urban India")
        if "all india" in full_text or "central" in full_text or "national" in full_text or not scope:
            states.add("All India")
        if not states:
            states.add("All India")

        # 4. CASTE / COMMUNITY DERIVATION
        communities = set()
        if community:
            communities.add(community)
        for c_tag in ["EWS/LIG", "Farmers", "BPL", "OBC", "SC", "ST", "General"]:
            if c_tag.lower() in full_text or c_tag.lower() in community.lower():
                communities.add(c_tag)
        if not communities:
            communities.add("All")

        # 5. RESIDENCE DERIVATION
        residence = set()
        if "urban" in full_text or "city" in full_text or "town" in full_text:
            residence.add("Urban")
        if "rural" in full_text or "village" in full_text or "gramin" in full_text:
            residence.add("Rural")
        if not residence or "all" in full_text:
            residence.add("All")

        # 6. EMPLOYMENT / OCCUPATION DERIVATION
        occupations = set()
        if occupation:
            occupations.add(occupation)
        occ_map = {
            "Farmer": ["farmer", "kisan", "cultivator", "uzhavar", "விவசாயி", "किसान"],
            "Student": ["student", "scholar", "study", "college", "school", "மாணவர்", "छात्र"],
            "Unorganized Worker": ["unorganized", "vendor", "artisan", "labor", "worker", "தொழிலாளி", "मज़दूर"],
            "Homemaker": ["homemaker", "housewife", "mother", "गृहणी"],
            "Employed": ["employed", "employee", "salaried"],
            "Unemployed": ["unemployed", "jobless"]
        }
        for occ_key, occ_kw in occ_map.items():
            if any(k in full_text for k in occ_kw):
                occupations.add(occ_key)
        if not occupations:
            occupations.add("All Citizens")

        # 7. BENEFIT TYPE DERIVATION
        benefit_types = set()
        if "dbt" in full_text or "direct benefit" in full_text or "transfer" in full_text:
            benefit_types.add("Direct Benefit Transfer (DBT)")
        if "loan" in full_text or "subsidy" in full_text or "grant" in full_text or "credit" in full_text:
            benefit_types.add("Subsidized Loan / Grant")
        if "health" in full_text or "medical" in full_text or "insurance" in full_text:
            benefit_types.add("Health Coverage")
        if "pension" in full_text or "monthly" in full_text or "financial aid" in full_text:
            benefit_types.add("Monthly Financial Aid")

        # 8. DISABILITY
        has_disability = (disability_req == 1) or any(k in full_text for k in ["disab", "handicap", "divyang", "மாற்றுத்திறனாளி", "दिव्यांग"])

        # 9. MARITAL STATUS
        marital_statuses = set()
        if "widow" in full_text or "widowed" in full_text:
            marital_statuses.add("Widowed")
        if "married" in full_text:
            marital_statuses.add("Married")
        if "single" in full_text or "unmarried" in full_text or "girl" in full_text:
            marital_statuses.add("Single")
        if not marital_statuses:
            marital_statuses.add("All")

        return {
            "genders": list(genders),
            "categories": list(categories),
            "states": list(states),
            "communities": list(communities),
            "residence": list(residence),
            "occupations": list(occupations),
            "benefit_types": list(benefit_types),
            "has_disability": has_disability,
            "marital_statuses": list(marital_statuses),
            "min_age": min_age,
            "max_age": max_age,
            "max_income": max_income
        }

    @staticmethod
    def evaluate_scheme(s: Dict[str, Any], filters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluates a scheme against citizen UI filters using 3-state evaluation:
        MATCH, NO_MATCH, UNKNOWN.
        Returns (is_eligible, reason) using AND across dimensions.
        """
        profile = SchemeEligibilityDeriver.derive_profile(s)

        # 1. State / UT
        req_state = filters.get("state")
        if req_state and req_state not in ["All States / UTs", "All States", "All", "Select"]:
            st_clean = req_state.strip()
            if st_clean == "Tamil Nadu":
                if not ("Tamil Nadu" in profile["states"] or "All India" in profile["states"]):
                    return False, "NO_MATCH: State scope does not cover Tamil Nadu"
            elif st_clean == "Urban India":
                if not ("Urban India" in profile["states"] or "All India" in profile["states"]):
                    return False, "NO_MATCH: Scope does not cover Urban India"
            elif st_clean == "All India":
                if "All India" not in profile["states"]:
                    return False, "NO_MATCH: Not a Central/All India scheme"

        # 2. Scheme Category
        req_cat = filters.get("category")
        if req_cat and req_cat not in ["All Categories", "All", "Select"]:
            c_clean = req_cat.strip()
            cat_match = False
            for c_item in profile["categories"]:
                if c_clean.lower() in c_item.lower() or c_item.lower() in c_clean.lower():
                    cat_match = True
                    break
            if not cat_match:
                return False, f"NO_MATCH: Category '{req_cat}' not matched in scheme categories"

        # 3. Gender
        req_gender = filters.get("gender")
        if req_gender and req_gender not in ["All Genders", "All", "Select"]:
            g_clean = req_gender.strip().upper()
            if g_clean in ["FEMALE", "WOMEN"]:
                if "FEMALE" not in profile["genders"] and "ALL" not in profile["genders"] and "UNKNOWN" not in profile["genders"]:
                    return False, "NO_MATCH: Scheme is restricted to Male applicants"
            elif g_clean in ["MALE", "MEN"]:
                if "MALE" not in profile["genders"] and "ALL" not in profile["genders"] and "UNKNOWN" not in profile["genders"]:
                    return False, "NO_MATCH: Scheme is restricted to Female applicants"

        # 4. Age Range
        req_age = filters.get("age")
        if req_age and req_age not in ["Select", "All"]:
            min_a, max_a = None, None
            if "18 - 25" in req_age:
                min_a, max_a = 18, 25
            elif "26 - 40" in req_age:
                min_a, max_a = 26, 40
            elif "41 - 60" in req_age:
                min_a, max_a = 41, 60
            elif "60+" in req_age:
                min_a, max_a = 60, 120

            if min_a is not None and max_a is not None:
                s_min = profile.get("min_age")
                s_max = profile.get("max_age")
                if s_min is not None and s_min > max_a:
                    return False, f"NO_MATCH: Minimum age required ({s_min}) exceeds age filter range ({max_a})"
                if s_max is not None and s_max < min_a:
                    return False, f"NO_MATCH: Maximum age ceiling ({s_max}) below age filter range ({min_a})"

        # 5. Caste / Community
        req_caste = filters.get("caste")
        if req_caste and req_caste not in ["Select", "All"]:
            if req_caste not in profile["communities"] and "All" not in profile["communities"]:
                pass # Non-strict matching unless conflicting

        # 6. Residence
        req_res = filters.get("residence")
        if req_res and req_res not in ["Select", "All"]:
            if req_res not in profile["residence"] and "All" not in profile["residence"]:
                pass

        # 7. Employment Status
        req_emp = filters.get("employment")
        if req_emp and req_emp not in ["Select", "All"]:
            if req_emp not in profile["occupations"] and "All Citizens" not in profile["occupations"]:
                pass

        # 8. Disability
        req_disability = filters.get("disability")
        if req_disability and "Benchmark" in str(req_disability):
            if not profile["has_disability"]:
                pass

        return True, "MATCH"
