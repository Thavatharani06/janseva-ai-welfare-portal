import re

def parse_multilingual_voice_text(text: str):
    if not text:
        return {"name": "", "district": "", "mobile": "", "income": ""}

    clean = text.strip()
    
    # 1. Clean out placeholder hints if present in input string
    clean = re.sub(r'English example:.*', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'Tamil example:.*', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'Type or dictate.*', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = clean.strip()
    
    if not clean:
        return {"name": "", "district": "", "mobile": "", "income": ""}

    # 2. Extract Mobile Number (10 digits starting with 6-9)
    mob_match = re.search(r'\b[6-9]\d{9}\b', clean)
    mobile = mob_match.group(0) if mob_match else ""

    # Remove mobile number from text before searching for income to avoid false matches
    text_no_mobile = clean
    if mobile:
        text_no_mobile = clean.replace(mobile, " ")

    # 3. Extract Income (INR)
    income = ""
    # Lakhs check (e.g. 1.5 lakh / 2.5 lakhs / 2 லட்சம்)
    inc_lakh = re.search(r'([\d\.]+)\s*(?:lakh|lakhs|லட்சம்)', text_no_mobile, re.IGNORECASE)
    if inc_lakh:
        try:
            val = float(inc_lakh.group(1))
            income = str(int(val * 100000))
        except:
            pass

    if not income:
        # Keyword-based income search
        inc_match = re.search(
            r'(?:income|annual income|income is|salary|வருமானம்|வருட வருமானம்|வருமான|ரூபாய்|rs\.?|inr)\s*[:\s\-]?\s*(\d{4,8})',
            text_no_mobile,
            re.IGNORECASE
        )
        if inc_match:
            income = inc_match.group(1)
        else:
            # Standalone 5-7 digit number (e.g. 180000, 150000, 250000)
            standalone_inc = re.search(r'\b[1-9]\d{4,6}\b', text_no_mobile)
            if standalone_inc:
                income = standalone_inc.group(0)

    # 4. District Matching (Tamil & English - 38 TN Districts)
    districts_map = {
        "madurai": "Madurai", "மதுரை": "Madurai",
        "chennai": "Chennai", "சென்னை": "Chennai",
        "coimbatore": "Coimbatore", "கோவை": "Coimbatore", "கோயம்புத்தூர்": "Coimbatore",
        "trichy": "Tiruchirappalli", "tiruchirappalli": "Tiruchirappalli", "திருச்சி": "Tiruchirappalli", "திருச்சிராப்பள்ளி": "Tiruchirappalli",
        "salem": "Salem", "சேலம்": "Salem",
        "tirunelveli": "Tirunelveli", "திருநெல்வேலி": "Tirunelveli",
        "erode": "Erode", "ஈரோடு": "Erode",
        "vellore": "Vellore", "வேலூர்": "Vellore",
        "thanjavur": "Thanjavur", "தஞ்சாவூர்": "Thanjavur", "தஞ்சை": "Thanjavur",
        "dindigul": "Dindigul", "திண்டுக்கல்": "Dindigul",
        "kanchipuram": "Kanchipuram", "காஞ்சிபுரம்": "Kanchipuram",
        "kanyakumari": "Kanyakumari", "கன்னியாகுமரி": "Kanyakumari",
        "tiruppur": "Tiruppur", "திருப்பூர்": "Tiruppur",
        "cuddalore": "Cuddalore", "கடலூர்": "Cuddalore",
        "dharmapuri": "Dharmapuri", "தர்மபுரி": "Dharmapuri",
        "karur": "Karur", "கரூர்": "Karur",
        "krishnagiri": "Krishnagiri", "கிருஷ்ணகிரி": "Krishnagiri",
        "nagapattinam": "Nagapattinam", "நாகப்பட்டினம்": "Nagapattinam",
        "namakkal": "Namakkal", "நாமக்கல்": "Namakkal",
        "nilgiris": "Nilgiris", "ooty": "Nilgiris", "நீலகிரி": "Nilgiris", "ஊட்டி": "Nilgiris",
        "perambalur": "Perambalur", "பெரம்பலூர்": "Perambalur",
        "pudukkottai": "Pudukkottai", "புதுக்கோட்டை": "Pudukkottai",
        "ramanathapuram": "Ramanathapuram", "இராமநாதபுரம்": "Ramanathapuram",
        "ranipet": "Ranipet", "ராணிப்பேட்டை": "Ranipet",
        "sivaganga": "Sivaganga", "சிவங்கை": "Sivaganga", "சிவ கங்கை": "Sivaganga",
        "tenkasi": "Tenkasi", "தென்காசி": "Tenkasi",
        "theni": "Theni", "தேனி": "Theni",
        "thoothukudi": "Thoothukudi", "tuticorin": "Thoothukudi", "தூத்துக்குடி": "Thoothukudi",
        "tirupathur": "Tirupathur", "திருப்பத்தூர்": "Tirupathur",
        "tiruvallur": "Tiruvallur", "திருவள்ளூர்": "Tiruvallur",
        "tiruvannamalai": "Tiruvannamalai", "திருவண்ணாமலை": "Tiruvannamalai",
        "tiruvarur": "Tiruvarur", "திருவாரூர்": "Tiruvarur",
        "viluppuram": "Viluppuram", "விழுப்புரம்": "Viluppuram",
        "virudhunagar": "Virudhunagar", "விருதுநகர்": "Virudhunagar"
    }

    found_district = ""
    clean_lower = clean.lower()
    for k, v in districts_map.items():
        if k in clean_lower:
            found_district = v
            break

    # 5. Extract Applicant Name (Tamil & English)
    found_name = ""
    
    # Tamil Name Patterns using unicode range [\u0B80-\u0BFF]
    ta_name_match = re.search(
        r'(?:என்\s+பெயர்|பெயர்\s+ஆகும்|பெயர்\s+ஆனது|பெயர்)\s*[:\s\-]?\s*([\u0B80-\u0BFF]+)',
        clean
    )
    if ta_name_match:
        cand = ta_name_match.group(1).strip()
        if cand not in ["என்", "பெயர்", "மாவட்டம்", "அலைபேசி", "வருமானம்"]:
            found_name = cand

    if not found_name:
        # English Name Patterns: "my name is <NAME>", "i am <NAME>", "name is <NAME>", "applicant name <NAME>"
        en_name_match = re.search(
            r'(?:my\s+name\s+is|name\s+is|i\s+am|applicant\s+name)\s*[:\s\-]?\s*([A-Za-z]+)',
            clean,
            re.IGNORECASE
        )
        if en_name_match:
            cand = en_name_match.group(1).strip()
            stopwords = {"is", "my", "a", "the", "living", "example", "in", "from", "district", "mobile", "phone", "income"}
            if cand.lower() not in stopwords:
                found_name = cand.title()

    if not found_name:
        # Fallback Name Search: Check first capitalised/Tamil word before comma or keywords
        words = re.split(r'[,.\s]+', clean)
        for idx, w in enumerate(words):
            if w.lower() in ["name", "my", "i", "am", "is", "english", "tamil", "example"]:
                continue
            if re.match(r'^[A-Z][a-z]+$', w) and w.lower() not in {"living", "district", "mobile", "income", "from", "street", "road"}:
                found_name = w
                break
            elif re.match(r'^[\u0B80-\u0BFF]{2,}$', w) and w not in {"சென்னை", "மதுரை", "கோவை", "சேலம்", "அலைபேசி", "வருமானம்", "மாவட்டம்", "என்", "பெயர்"}:
                found_name = w
                break

    return {
        "name": found_name,
        "district": found_district,
        "mobile": mobile,
        "income": income
    }

# Test inputs
test_cases = [
    "My name is Suresh, living in Coimbatore district, mobile 9443123456, income 180000",
    "என் பெயர் செல்வம், சென்னை மாவட்டம், அலைபேசி 9840123456, வருமானம் 150000",
    "I am Ramesh from Madurai, phone 9876543210, annual income 2.5 lakhs",
    "என் பெயர் முருகன் மதுரை மாவட்டம் வருமானம் 200000 அலைபேசி 9765432109",
    "Praveen, Salem district, mobile 9988776655, income 120000"
]

for tc in test_cases:
    res = parse_multilingual_voice_text(tc)
    print("INPUT:", tc.encode('ascii', 'backslashreplace'))
    print("PARSED:", {k: v.encode('ascii', 'backslashreplace').decode('ascii') for k, v in res.items()})
    print("-" * 50)
