import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("janseva.electricity")

class ElectricityService:
    def __init__(self, catalog_path: Optional[str] = None):
        if not catalog_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            catalog_path = os.path.join(base_dir, "data", "master_electricity_benefits.json")
        
        self.catalog_path = catalog_path
        self.benefits = self._load_catalog()

    def _load_catalog(self) -> List[Dict[str, Any]]:
        possible_paths = [
            self.catalog_path,
            os.path.join(os.getcwd(), "backend", "data", "master_electricity_benefits.json"),
            os.path.join(os.getcwd(), "data", "master_electricity_benefits.json")
        ]
        for path in possible_paths:
            if path and os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load catalog from {path}: {e}")
        
        # Fallback default catalog
        return [
            {
                "benefit_id": "TN_DOMESTIC_ELECTRICITY_SUBSIDY",
                "name": "Tamil Nadu Domestic Electricity Subsidy",
                "service": "Electricity",
                "state": "Tamil Nadu",
                "beneficiary_category": "Domestic Consumer",
                "benefit_type": "Free electricity",
                "unit_limit": 100,
                "period": "bi-monthly",
                "eligibility_rules": {"state": "Tamil Nadu", "consumer_category": ["Domestic Consumer", "Domestic"]},
                "official_source": "Government of Tamil Nadu — Energy Department & TANGEDCO Tariff Orders",
                "source_url": "https://www.tangedco.gov.in"
            },
            {
                "benefit_id": "TN_HANDLOOM_FREE_ELECTRICITY",
                "name": "Tamil Nadu Free Electricity Scheme for Handloom Weavers",
                "service": "Electricity",
                "state": "Tamil Nadu",
                "beneficiary_category": "Handloom Weaver",
                "benefit_type": "Free electricity",
                "unit_limit": 200,
                "period": "bi-monthly",
                "eligibility_rules": {"state": "Tamil Nadu", "occupation": ["Handloom Weaver", "Handloom"]},
                "official_source": "Government of Tamil Nadu — Department of Handlooms, Handicrafts, Textiles and Khadi",
                "source_url": "https://www.tn.gov.in/handlooms"
            },
            {
                "benefit_id": "TN_POWERLOOM_FREE_ELECTRICITY",
                "name": "Tamil Nadu Free Electricity Scheme for Powerloom Weavers",
                "service": "Electricity",
                "state": "Tamil Nadu",
                "beneficiary_category": "Powerloom Weaver",
                "benefit_type": "Free electricity",
                "unit_limit": 750,
                "period": "bi-monthly",
                "eligibility_rules": {"state": "Tamil Nadu", "occupation": ["Powerloom Weaver", "Powerloom"]},
                "official_source": "Government of Tamil Nadu — Department of Handlooms, Handicrafts, Textiles and Khadi",
                "source_url": "https://www.tn.gov.in/handlooms"
            }
        ]

    def evaluate_eligibility(
        self,
        profile: Dict[str, Any],
        consumer_type: Optional[str] = None,
        occupation: Optional[str] = None,
        state: Optional[str] = None,
        target_benefit_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates citizen eligibility against structured electricity benefits catalog.
        
        Returns status: ELIGIBLE | NOT_ELIGIBLE | MORE_INFORMATION_REQUIRED
        """
        # Determine effective parameters
        eff_state = state or profile.get("state") or profile.get("district_state") or profile.get("personal_info", {}).get("district_state", {}).get("value") or "Tamil Nadu"
        eff_occupation = occupation or profile.get("occupation") or profile.get("personal_info", {}).get("occupation", {}).get("value")
        eff_consumer_type = consumer_type or profile.get("consumer_type")

        # Normalize UNKNOWN values
        if isinstance(eff_occupation, str) and eff_occupation.strip().upper() in ["UNKNOWN", "SELECT", "NONE", ""]:
            eff_occupation = None
        if isinstance(eff_consumer_type, str) and eff_consumer_type.strip().upper() in ["UNKNOWN", "SELECT", "NONE", ""]:
            eff_consumer_type = None

        # State check (Tamil Nadu specific catalog)
        if eff_state and "TAMIL NADU" not in str(eff_state).upper() and "TN" not in str(eff_state).upper():
            return {
                "status": "NOT_ELIGIBLE",
                "title": "Not Currently Eligible",
                "summary": "Tamil Nadu electricity subsidy rules apply to Tamil Nadu residents only.",
                "evaluated_benefits": [],
                "failed_rules": [
                    f"State constraint failed: Citizen state is '{eff_state}', but documented benefits require 'Tamil Nadu'."
                ],
                "official_sources": [b["official_source"] for b in self.benefits]
            }

        # If neither occupation nor consumer category is provided/known
        if not eff_occupation and not eff_consumer_type:
            return {
                "status": "MORE_INFORMATION_REQUIRED",
                "title": "More Information Required",
                "summary": "We need your beneficiary category or occupation to evaluate exact electricity benefit eligibility.",
                "missing_fields": [
                    {"field": "consumer_category", "label": "Electricity Consumer Type", "options": ["Domestic Consumer", "Handloom Weaver", "Powerloom Weaver", "Other"]},
                    {"field": "occupation", "label": "Occupation", "options": ["Handloom Weaver", "Powerloom Weaver", "Student", "Worker", "Other"]}
                ],
                "question": "Are you a handloom weaver, powerloom weaver, domestic consumer, or another category?",
                "official_sources": [b["official_source"] for b in self.benefits]
            }

        # Check matched benefits
        evaluated_benefits = []
        occ_upper = (eff_occupation or "").upper()
        cons_upper = (eff_consumer_type or "").upper()

        # Handloom Weaver Check
        if "HANDLOOM" in occ_upper or "HANDLOOM" in cons_upper:
            b_item = next(b for b in self.benefits if b["benefit_id"] == "TN_HANDLOOM_FREE_ELECTRICITY")
            evaluated_benefits.append({
                "benefit_id": b_item["benefit_id"],
                "name": b_item["name"],
                "unit_limit": b_item["unit_limit"],
                "period": b_item["period"],
                "beneficiary_category": "Handloom Weaver",
                "status": "ELIGIBLE",
                "matching_rules": [
                    "✓ Resident of Tamil Nadu",
                    "✓ Consumer category / occupation: Handloom Weaver",
                    "✓ Free electricity up to 200 units bi-monthly"
                ],
                "official_source": b_item["official_source"],
                "source_url": b_item["source_url"]
            })

        # Powerloom Weaver Check
        if "POWERLOOM" in occ_upper or "POWERLOOM" in cons_upper:
            b_item = next(b for b in self.benefits if b["benefit_id"] == "TN_POWERLOOM_FREE_ELECTRICITY")
            evaluated_benefits.append({
                "benefit_id": b_item["benefit_id"],
                "name": b_item["name"],
                "unit_limit": b_item["unit_limit"],
                "period": b_item["period"],
                "beneficiary_category": "Powerloom Weaver",
                "status": "ELIGIBLE",
                "matching_rules": [
                    "✓ Resident of Tamil Nadu",
                    "✓ Consumer category / occupation: Powerloom Weaver",
                    "✓ Free electricity up to 750 units bi-monthly"
                ],
                "official_source": b_item["official_source"],
                "source_url": b_item["source_url"]
            })

        # Standard Domestic Subsidy Check (All Domestic Consumers in TN get 100 free units)
        dom_item = next(b for b in self.benefits if b["benefit_id"] == "TN_DOMESTIC_ELECTRICITY_SUBSIDY")
        evaluated_benefits.append({
            "benefit_id": dom_item["benefit_id"],
            "name": dom_item["name"],
            "unit_limit": dom_item["unit_limit"],
            "period": dom_item["period"],
            "beneficiary_category": "Domestic Consumer",
            "status": "ELIGIBLE",
            "matching_rules": [
                "✓ Resident of Tamil Nadu",
                "✓ Domestic electricity consumer",
                "✓ Free electricity up to 100 units bi-monthly"
            ],
            "official_source": dom_item["official_source"],
            "source_url": dom_item["source_url"]
        })

        # If a specific target benefit was requested (e.g. handloom 200 units) and user is not handloom weaver
        if target_benefit_id == "TN_HANDLOOM_FREE_ELECTRICITY" and not ("HANDLOOM" in occ_upper or "HANDLOOM" in cons_upper):
            return {
                "status": "NOT_ELIGIBLE",
                "title": "Not Currently Eligible for Handloom Benefit",
                "summary": "The 200-unit free electricity benefit is specifically documented for handloom weavers. Your current profile does not show that beneficiary category.",
                "evaluated_benefits": evaluated_benefits,
                "failed_rules": [
                    f"Occupation / Consumer category constraint: Profile is '{eff_occupation or eff_consumer_type}', which does not match 'Handloom Weaver'."
                ],
                "alternative_benefit": "You remain eligible for the 100-unit bi-monthly domestic electricity subsidy in Tamil Nadu.",
                "official_sources": [dom_item["official_source"]]
            }

        return {
            "status": "ELIGIBLE",
            "title": "✓ You may be eligible",
            "summary": f"Based on your profile ({eff_state}, {eff_occupation or eff_consumer_type}), you qualify for Tamil Nadu electricity benefits.",
            "evaluated_benefits": evaluated_benefits,
            "failed_rules": [],
            "official_sources": list(set(b["official_source"] for b in evaluated_benefits))
        }

    def answer_conversational_query(
        self,
        query: str,
        profile: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Grounded AI Assistant handler for natural language electricity queries.
        """
        q_lower = query.lower()

        # Extract parameters from query if mentioned directly
        query_occ = None
        if "handloom" in q_lower or "கைத்தறி" in q_lower or "हथकरघा" in q_lower:
            query_occ = "Handloom Weaver"
        elif "powerloom" in q_lower or "விசைத்தறி" in q_lower or "पावरलूम" in q_lower:
            query_occ = "Powerloom Weaver"
        elif "domestic" in q_lower or "வீட்டு" in q_lower or "घरेलू" in q_lower:
            query_occ = "Domestic Consumer"

        # Evaluate
        target_b = "TN_HANDLOOM_FREE_ELECTRICITY" if ("200" in q_lower or "handloom" in q_lower or "கைத்தறி" in q_lower) else None
        res = self.evaluate_eligibility(profile, occupation=query_occ, target_benefit_id=target_b)

        # Formulate grounded response based on evaluation result
        if res["status"] == "MORE_INFORMATION_REQUIRED":
            if language in ("ta", "ta-IN", "தமிழ்"):
                response_text = "நிச்சயமாக. உங்கள் சுயவிவரத்தின் அடிப்படையில் மின்சார சலுகைகளை கணக்கிட முடியும். நீங்கள் கைத்தறி நெசவாளரா, விசைத்தறி நெசவாளரா, அல்லது சாதாரண வீட்டு நுகர்வோரா என்பதை தெரிவிக்க முடியுமா?"
            elif language in ("hi", "hi-IN", "हिन्दी"):
                response_text = "जी बिल्कुल। आपकी पात्रता जांचने के लिए मुझे आपकी श्रेणी या व्यवसाय की जानकारी चाहिए। क्या आप हथकरघा बुनकर हैं, पावरलूम बुनकर हैं या घरेलू उपभोक्ता?"
            else:
                response_text = "Sure. I can check the electricity benefits available based on your profile. I need your electricity consumer category or occupation (e.g., Handloom Weaver, Powerloom Weaver, or Domestic Consumer)."
        
        elif res["status"] == "NOT_ELIGIBLE":
            if language in ("ta", "ta-IN", "தமிழ்"):
                response_text = f"அந்த 200 யூனிட் இலவச மின்சார சலுகை கைத்தறி நெசவாளர்களுக்கு மட்டுமே பொருந்தும். உங்கள் தற்போதைய சுயவிவரம் அந்த பிரிவை காட்டவில்லை, இருப்பினும் அனைத்து தமிழ்நாட்டு வீட்டு நுகர்வோருக்கும் 100 யூனிட் இலவச மின்சாரம் கிடைக்கும்."
            elif language in ("hi", "hi-IN", "हिन्दी"):
                response_text = f"200 यूनिट की मुफ्त बिजली योजना विशेष रूप से हथकरघा बुनकरों के लिए है। आपकी वर्तमान प्रोफ़ाइल में वह श्रेणी दर्ज नहीं है, हालांकि तमिलनाडु के सभी घरेलू उपभोक्ताओं को 100 यूनिट मुफ्त बिजली मिलती है।"
            else:
                response_text = f"{res['summary']} {res.get('alternative_benefit', '')}"

        else: # ELIGIBLE
            b_list = res.get("evaluated_benefits", [])
            primary_b = b_list[0] if b_list else {}
            limit = primary_b.get("unit_limit", 100)
            b_name = primary_b.get("name", "Tamil Nadu Electricity Subsidy")

            if language in ("ta", "ta-IN", "தமிழ்"):
                response_text = f"உங்கள் சுயவிவரத்தின் அடிப்படையில், நீங்கள் '{b_name}' திட்டத்திற்கு தகுதியானவர். இதன்படி உங்களுக்கு இரண்டு மாதங்களுக்கு {limit} யூனிட் வரை இலவச மின்சாரம் கிடைக்கும்."
            elif language in ("hi", "hi-IN", "हिन्दी"):
                response_text = f"आपकी प्रोफ़ाइल के अनुसार, आप '{b_name}' के तहत प्रति दो महीने में {limit} यूनिट तक मुफ्त बिजली प्राप्त करने के पात्र हैं।"
            else:
                response_text = f"You are eligible for {b_name}, which provides up to {limit} units of free electricity every two months. This is grounded in official Tamil Nadu government benefit rules."

        return {
            "response": response_text,
            "status": res["status"],
            "evaluation_result": res,
            "official_source": res.get("official_sources", ["Government of Tamil Nadu"])[0]
        }
