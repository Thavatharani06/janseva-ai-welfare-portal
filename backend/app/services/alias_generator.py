import re
from typing import List

class AliasGenerator:
    @staticmethod
    def generate_aliases(scheme_title: str) -> List[str]:
        """
        Auto-generates acronyms and synonyms from scheme title.
        Example: "Pradhan Mantri Awas Yojana" -> ["PMAY", "Awas Yojana", "Housing Scheme"]
        """
        aliases = []
        clean_title = re.sub(r"[^\w\s-]", "", scheme_title).strip()

        # 1. Generate initials (acronyms)
        # Match capital letters or start of words (e.g. "Pradhan Mantri Awas Yojana" -> PMAY)
        words = clean_title.split()
        acronym = "".join([w[0].upper() for w in words if w[0].isupper() or w[0].isalpha()])
        if len(acronym) >= 3:
            aliases.append(acronym)
            # Handle standard sub-acronyms (e.g. PMAY-U / PMAY-G)
            if "urban" in scheme_title.lower():
                aliases.append(f"{acronym}-U")
            elif "gramin" in scheme_title.lower() or "rural" in scheme_title.lower():
                aliases.append(f"{acronym}-G")

        # 2. Add domain synonyms based on keywords
        lower_title = scheme_title.lower()
        if "housing" in lower_title or "awas" in lower_title:
            aliases.extend(["Housing Scheme", "House Subsidy", "Home Grant", "Awas Yojana"])
        if "farmer" in lower_title or "kisan" in lower_title:
            aliases.extend(["Farmer Subsidy", "Agriculture Support", "Kisan Scheme"])
        if "scholarship" in lower_title or "education" in lower_title:
            aliases.extend(["Education Scholarship", "College Grant", "Student Aid"])
        if "pension" in lower_title:
            aliases.extend(["Pension Scheme", "Monthly Pension", "Social Security Grant"])
        if "women" in lower_title or "magalir" in lower_title or "urimai" in lower_title:
            aliases.extend(["Women Empowerment", "Magalir Scheme", "Monthly Cash for Women"])

        # Deduplicate
        return list(set(aliases))
