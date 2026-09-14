import re
from typing import Dict, Any

class RuleExtractor:
    @staticmethod
    def extract_eligibility_limits(text: str) -> Dict[str, Any]:
        """
        Parses raw text strings to extract structured eligibility rules:
        - min_age, max_age
        - max_income
        - gender_restriction
        - target_occupation
        - target_community
        """
        clean_text = text.lower()
        
        # Default fallback values
        rules = {
            "min_age": 0,
            "max_age": 120,
            "max_income": None,
            "gender_restriction": "All",
            "target_occupation": "All",
            "target_community": "All"
        }

        # 1. Age extraction e.g. "above 21 years", "age 18 to 60", "between 18 and 70"
        age_between = re.search(r"age[sd]?\s*(?:between)?\s*(\d+)\s*(?:to|and|-)\s*(\d+)", clean_text)
        if age_between:
            rules["min_age"] = int(age_between.group(1))
            rules["max_age"] = int(age_between.group(2))
        else:
            above_age = re.search(r"(?:above|greater than|at least)\s*(\d+)", clean_text)
            if above_age:
                rules["min_age"] = int(above_age.group(1))
            
            below_age = re.search(r"(?:below|under|less than|up to)\s*(\d+)\s*(?:years|yrs)", clean_text)
            if below_age:
                rules["max_age"] = int(below_age.group(1))


        # 2. Income extraction e.g. "income below 2.5 lakh", "income under 3,00,000", "income up to 120000"
        income_match = re.search(r"(?:income|earnings)\s*(?:below|under|less than|up to|maximum of)\s*(?:rs\.?|inr)?\s*([\d,.]+)\s*(lakh|lakhs|l)?", clean_text)
        if income_match:
            value_str = income_match.group(1).replace(",", "")
            is_lakh = bool(income_match.group(2))
            try:
                value = float(value_str)
                if is_lakh or value < 1000:
                    rules["max_income"] = value * 100000.0
                else:
                    rules["max_income"] = value
            except ValueError:
                pass

        # 3. Gender extraction e.g. "women", "female", "only girls", "male only", "men above"
        if "women" in clean_text or "female" in clean_text or "girl" in clean_text:
            rules["gender_restriction"] = "Female"
        elif "men " in clean_text or "male only" in clean_text or "boys" in clean_text:
            rules["gender_restriction"] = "Male"

        # 4. Occupation extraction e.g. "farmer", "student", "unorganized labor", "artisan"
        if "farmer" in clean_text or "agricultural" in clean_text:
            rules["target_occupation"] = "Farmer"
        elif "student" in clean_text or "scholarship" in clean_text:
            rules["target_occupation"] = "Student"
        elif "weaver" in clean_text or "artisan" in clean_text:
            rules["target_occupation"] = "Artisan"
        elif "unorganized" in clean_text or "labor" in clean_text:
            rules["target_occupation"] = "Unorganized Worker"

        # 5. Community extraction e.g. "sc/st", "obc", "minority"
        if "sc/st" in clean_text or "scheduled caste" in clean_text:
            rules["target_community"] = "SC/ST"
        elif "obc" in clean_text:
            rules["target_community"] = "OBC"
        elif "minority" in clean_text:
            rules["target_community"] = "Minority"

        return rules
