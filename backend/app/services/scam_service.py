import re
from typing import Dict, Any

SCAM_KEYWORDS = [
    r"pay money", r"bribe", r"fee for scheme", r"agent fee", r"guaranteed scheme",
    r"give 500", r"give 1000", r"give cash", r"lakhs fee", r"unofficial agent",
    r"பணம் கேட்கிறார்", r"லஞ்சம்", r"கமிஷன்", r"முன்பணம்", r"ஏஜெண்ட்"
]

class ScamService:
    @staticmethod
    def detect_scam(query: str) -> Dict[str, Any]:
        """
        Analyzes query for scam indicators and returns warning details if suspicious.
        """
        clean_query = query.lower()
        flagged = False
        matched_triggers = []

        for pattern in SCAM_KEYWORDS:
            if re.search(pattern, clean_query):
                flagged = True
                matched_triggers.append(pattern)

        if flagged:
            return {
                "scam_flagged": True,
                "warning_title": "⚠️ ALERT: Potential Government Welfare Scam Detected!",
                "warning_message": "Government welfare schemes are 100% FREE. No official government officer or agent will ever ask for cash payments, commissions, or processing fees to approve your application.",
                "official_helplines": [
                    {"name": "Tamil Nadu Citizen Helpline", "number": "1100"},
                    {"name": "PM-KISAN Fraud Helpline", "number": "155261"},
                    {"name": "National Anti-Corruption Bureau", "number": "1064"}
                ],
                "official_portals": [
                    {"title": "TN e-Sevai Portal", "url": "https://tnesevai.tn.gov.in"},
                    {"title": "National Portal of India", "url": "https://india.gov.in"}
                ],
                "matched_triggers": matched_triggers
            }

        return {"scam_flagged": False}
