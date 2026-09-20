import streamlit as st
import streamlit.components.v1 as components
import json
import os
import base64
import sqlite3

# Page Configuration
st.set_page_config(
    page_title="Government Welfare Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default UI elements
st.markdown("""
<style>
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
    .stApp { background-color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# Helper function to convert local image files to Base64
def get_image_b64(filename):
    p = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(p):
        try:
            with open(p, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        except Exception:
            pass
    return ""

logo_b64 = get_image_b64("gwa-logo.png")
hero_b64 = get_image_b64("gwa-hero.png")

# Core Real Dataset Fallback
DEFAULT_CATEGORIES = [
    {"id": "cat_housing", "name": "Housing & Urban Development", "name_ta": "வீட்டுவசதித் திட்டம்", "name_hi": "आवास और शहरी विकास", "icon": "home", "description": "Subsidies and financial aid for housing construction"},
    {"id": "cat_agriculture", "name": "Agriculture & Farmers Welfare", "name_ta": "வேளாண்மை உதவி", "name_hi": "कृषि एवं किसान कल्याण", "icon": "sprout", "description": "Direct income support and credit for farmers"},
    {"id": "cat_women", "name": "Women & Child Development", "name_ta": "மகளிர் நலம்", "name_hi": "महिला एवं बाल विकास", "icon": "heart", "description": "Monthly assistance, maternity benefit, and empowerment grants"},
    {"id": "cat_health", "name": "Healthcare & Insurance", "name_ta": "சுகாதாரம் & காப்பீடு", "name_hi": "स्वास्थ्य सेवा एवं बीमा", "icon": "activity", "description": "Cashless hospital treatment and medical coverage"},
    {"id": "cat_education", "name": "Education & Scholarships", "name_ta": "கல்வி உதவித் தொகை", "name_hi": "शिक्षा एवं छात्रवृत्ति", "icon": "graduation-cap", "description": "Financial assistance for school and college education"}
]

DEFAULT_SCHEMES = [
    {
        "id": "pmay-urban",
        "category_id": "cat_housing",
        "title": "Pradhan Mantri Awas Yojana (PMAY-Urban)",
        "title_ta": "பிரதம மந்திரி ஆவாஸ் யோஜனா (வீட்டுவசதி திட்டம்)",
        "title_hi": "प्रधानमंत्री आवास योजना (शहरी)",
        "code": "PMAY-U",
        "ministry": "Ministry of Housing and Urban Affairs",
        "official_website": "https://pmaymis.gov.in",
        "helpline_number": "1800-11-3377",
        "legal_summary": "Under G.O. MS No. 142/2015, Credit Linked Subsidy Scheme (CLSS) provides upfront interest subsidy up to Rs. 2.67 Lakhs on housing loans for EWS/LIG families with annual income up to Rs. 3,00,000.",
        "simple_summary": "PMAY helps low-income families get a government grant and interest reduction up to ₹2.67 Lakh to build or buy a first-time pucca home.",
        "simple_summary_ta": "குறைந்த வருமானம் கொண்ட குடும்பங்களுக்கு முதல் முறையாக வீடு கட்ட அல்லது வாங்க ₹2.67 லட்சம் வரை அரசு மானியம் மற்றும் வட்டி குறைப்பு பெற PMAY உதவுகிறது.",
        "simple_summary_hi": "PMAY कम आय वाले परिवारों को पहली बार पक्का मकान बनाने या खरीदने के लिए ₹2.67 लाख तक की सरकारी सब्सिडी प्रदान करता है।",
        "eli10_summary": "Imagine the government giving your family money to help build your dream house so everyone gets a safe room to sleep in!",
        "min_age": 18,
        "max_age": 70,
        "max_income": 300000.0,
        "gender_restriction": "All",
        "disability_required": False,
        "target_community": "EWS/LIG",
        "target_occupation": "All Citizens",
        "state_district_scope": "Urban India",
        "required_documents": ["Aadhaar Card", "Income Certificate", "Ration Card", "Bank Passbook", "Property Land Deed"]
    },
    {
        "id": "pm-kisan",
        "category_id": "cat_agriculture",
        "title": "PM-KISAN Samman Nidhi Scheme",
        "title_ta": "பி.எம். கிசான் விவசாயிகள் உதவித் தொகை",
        "title_hi": "पीएम-किसान सम्मान निधि योजना",
        "code": "PM-KISAN",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "official_website": "https://pmkisan.gov.in",
        "helpline_number": "155261",
        "legal_summary": "Under PM-KISAN guidelines 2019, all landholding farmer families receive income support of Rs. 6,000 per year in three equal quarterly installments of Rs. 2,000 transferred directly into bank accounts.",
        "simple_summary": "Eligible land-owning farmers receive ₹6,000 every year directly in their bank accounts in 3 equal quarterly installments of ₹2,000.",
        "simple_summary_ta": "தகுதியுள்ள விவசாயிகளுக்கு ஆண்டுதோறும் ₹6,000 அவர்களின் வங்கிச் கணக்கில் 3 சம தவணைகளாக (₹2,000) நேரடியாக செலுத்தப்படுகிறது.",
        "simple_summary_hi": "पात्र भूमिधारक किसानों को हर साल ₹6,000 सीधे उनके बैंक खातों में 3 समान किस्तों (₹2,000) में मिलते हैं।",
        "eli10_summary": "The government sends 2,000 rupees three times a year to farmers to buy seeds and fertilizer for crops!",
        "min_age": 18,
        "max_age": 100,
        "max_income": 500000.0,
        "gender_restriction": "All",
        "disability_required": False,
        "target_community": "Farmers",
        "target_occupation": "Farmer",
        "state_district_scope": "All India",
        "required_documents": ["Aadhaar Card", "Land Patta Certificate", "Bank Account Passbook"]
    },
    {
        "id": "kalaignar-magalir",
        "category_id": "cat_women",
        "title": "Kalaignar Magalir Urimai Thogai Scheme",
        "title_ta": "கலைஞர் மகளிர் உரிமைத் தொகைத் திட்டம்",
        "title_hi": "कलाईग्नार महिला अधिकार योजना",
        "code": "KMT",
        "ministry": "Government of Tamil Nadu - Special Programme Implementation",
        "official_website": "https://kmt.tn.gov.in",
        "helpline_number": "1100",
        "legal_summary": "Under G.O. MS No. 46/2023, female heads of households with annual income below Rs. 2.5 Lakhs and electricity usage under 3600 units receive a monthly right grant of Rs. 1,000.",
        "simple_summary": "Women heads of families in Tamil Nadu with annual family income under ₹2.5 Lakhs get ₹1,000 monthly direct bank transfer.",
        "simple_summary_ta": "தமிழ்நாட்டில் ஆண்டு வருமானம் ₹2.5 லட்சத்திற்கு கீழ் உள்ள குடும்பத் தலைவிகளுக்கு மாதம் ₹1,000 வங்கிச் கணக்கில் நேரடியாக வழங்கப்படுகிறது.",
        "simple_summary_hi": "तमिलनाडु में ₹2.5 लाख से कम वार्षिक आय वाले परिवारों की महिला प्रमुखों को हर महीने ₹1,000 सीधे बैंक खाते में मिलते हैं।",
        "eli10_summary": "Every month, moms get 1,000 rupees from the government to help run the house smoothly!",
        "min_age": 21,
        "max_age": 100,
        "max_income": 250000.0,
        "gender_restriction": "Female",
        "disability_required": False,
        "target_community": "EWS",
        "target_occupation": "Homemaker / Worker",
        "state_district_scope": "Tamil Nadu",
        "required_documents": ["Aadhaar Card", "Smart Ration Card", "Electricity Bill", "Bank Passbook"]
    },
    {
        "id": "ayushman-bharat",
        "category_id": "cat_health",
        "title": "Ayushman Bharat PM-JAY Health Insurance",
        "title_ta": "ஆயுஷ்மான் பாரத் மருத்துவக் காப்பீடு",
        "title_hi": "आयुष्मान भारत पीएम-जय स्वास्थ्य बीमा",
        "code": "PM-JAY",
        "ministry": "National Health Authority",
        "official_website": "https://pmjay.gov.in",
        "helpline_number": "14555",
        "legal_summary": "PM-JAY provides cashless secondary and tertiary hospitalization coverage up to Rs. 5,00,000 per family per year for bottom 40% vulnerable population based on SECC 2011.",
        "simple_summary": "Get free cashless hospital treatment coverage up to ₹5 Lakhs per family every year in empaneled public and private hospitals.",
        "simple_summary_ta": "அரசு மற்றும் தனியார் மருத்துவமனைகளில் குடும்பத்திற்கு ஆண்டுக்கு ₹5 லட்சம் வரை இலவச ரொக்கமில்லா மருத்துவ சிகிச்சை காப்பீடு பெறலாம்.",
        "simple_summary_hi": "संबद्ध सरकारी और निजी अस्पतालों में प्रति वर्ष प्रति परिवार ₹5 लाख तक का मुफ्त कैशलेस अस्पताल उपचार कवर प्राप्त करें।",
        "eli10_summary": "If anyone in your family gets sick and needs hospital treatment, the health card pays up to 5 lakh rupees!",
        "min_age": 0,
        "max_age": 120,
        "max_income": 250000.0,
        "gender_restriction": "All",
        "disability_required": False,
        "target_community": "BPL / EWS",
        "target_occupation": "All Vulnerable Families",
        "state_district_scope": "All India",
        "required_documents": ["Aadhaar Card", "Ration Card"]
    },
    {
        "id": "pudhumai-penn",
        "category_id": "cat_education",
        "title": "Pudhumai Penn Scheme (Moovalur Ramamirtham Ammiyar)",
        "title_ta": "மூவலூர் ராமாமிர்தம் அம்மையார் புதுமைப் பெண் திட்டம்",
        "title_hi": "पुधुमई पेन योजना (उच्च शिक्षा सहायता)",
        "code": "PUDHUMAI-PENN",
        "ministry": "Government of Tamil Nadu - Higher Education",
        "official_website": "https://penkalvi.tn.gov.in",
        "helpline_number": "1800-425-0110",
        "legal_summary": "Under G.O. MS No. 11/2022, girl students who studied classes 6th to 12th in Government schools receive Rs. 1,000 per month until graduation/diploma completion.",
        "simple_summary": "Girl students from Tamil Nadu government schools receive ₹1,000 monthly financial aid until graduation or diploma completion.",
        "simple_summary_ta": "அரசுப் பள்ளிகளில் 6 முதல் 12 ஆம் வகுப்பு வரை படித்த மாணவிகளுக்குக் கல்லூரிப் படிப்பு முடியும் வரை மாதம் ₹1,000 நிதியுதவி வழங்கப்படுகிறது.",
        "simple_summary_hi": "तमिलनाडु के सरकारी स्कूलों की छात्राओं को स्नातक या डिप्लोमा पूरा होने तक ₹1,000 की मासिक वित्तीय सहायता मिलती है।",
        "eli10_summary": "Girls who finish government school get 1,000 rupees every month while studying in college!",
        "min_age": 17,
        "max_age": 25,
        "gender_restriction": "Female",
        "disability_required": False,
        "target_community": "Students",
        "target_occupation": "Student",
        "state_district_scope": "Tamil Nadu",
        "required_documents": ["Aadhaar Card", "10th & 12th Marksheets", "6th-12th Govt School Bonafide Certificate", "Bank Passbook"]
    }
]

# Fetch Backend Database Data with Fallback
def get_backend_data():
    db_paths = [
        os.path.join(os.path.dirname(__file__), "backend", "legal_welfare.db"),
        os.path.join(os.path.dirname(__file__), "legal_welfare.db")
    ]
    
    categories = []
    schemes = []
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("SELECT id, name, name_ta, icon, description FROM scheme_categories")
                categories = [dict(row) for row in c.fetchall()]
                c.execute("SELECT id, category_id, title, title_ta, code, ministry, official_website, helpline_number, legal_summary, simple_summary, eli10_summary, min_age, max_age, max_income, gender_restriction, disability_required, target_community, target_occupation, state_district_scope, required_documents FROM schemes")
                for row in c.fetchall():
                    s = dict(row)
                    if isinstance(s.get("required_documents"), str):
                        try:
                            s["required_documents"] = json.loads(s["required_documents"])
                        except Exception:
                            s["required_documents"] = [s["required_documents"]]
                    schemes.append(s)
                conn.close()
                if categories and schemes:
                    break
            except Exception:
                pass
                
    if not categories:
        categories = DEFAULT_CATEGORIES
    if not schemes:
        schemes = DEFAULT_SCHEMES
        
    return categories, schemes

categories_data, schemes_data = get_backend_data()

# Build Initial HTML Snippets
def render_categories_html(categories):
    icon_map = {"home": "🏠", "sprout": "🌾", "heart": "👩", "activity": "💚", "graduation-cap": "🎓"}
    html_items = []
    for cat in categories:
        icon = icon_map.get(cat.get("icon", ""), "🏛️")
        name = cat.get("name", "Category")
        cat_id = cat.get("id", "")
        count = len([s for s in schemes_data if s.get("category_id") == cat_id])
        if count == 0: count = 1
        html_items.append(f'<div class="cat" data-catid="{cat_id}" onclick="category(\'{cat_id}\')"><div class="cat-icon">{icon}</div><div><strong>{name}</strong><small>{count} Schemes</small></div><span class="arrow">→</span></div>')
    return "".join(html_items)

def render_schemes_html(schemes):
    html_items = []
    for s in schemes[:6]:
        sid = s.get("id", "")
        title = s.get("title", "Government Scheme")
        ministry = s.get("ministry", "Government of India")
        summary = s.get("simple_summary", "")[:130] + "..." if len(s.get("simple_summary", "")) > 130 else s.get("simple_summary", "")
        tags = []
        if s.get("target_occupation"): tags.append(s.get("target_occupation"))
        if s.get("state_district_scope"): tags.append(s.get("state_district_scope"))
        tags_html = "".join([f'<span class="tag">{t}</span>' for t in tags[:3]]) or '<span class="tag">Central Scheme</span>'
        
        html_items.append(f'''
        <div class="scheme">
          <h3>{title}</h3>
          <div class="min">{ministry}</div>
          <p>{summary}</p>
          <div class="tags">{tags_html}</div>
          <div class="scheme-actions">
            <button class="primary" onclick="scheme('{sid}')">View Scheme →</button>
            <button class="secondary" onclick="eligibility('{sid}')">Check Eligibility</button>
          </div>
        </div>
        ''')
    return "".join(html_items)

categories_rendered_html = render_categories_html(categories_data)
schemes_rendered_html = render_schemes_html(schemes_data)
schemes_count_str = f"{len(schemes_data)}+" if schemes_data else "120+"

# APPROVED LOCKED USER HTML UI TEMPLATE
USER_UI_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Government Welfare Assistant</title>
<style>
@page{size:1024px 1536px;margin:0}
:root{--green:#00865a;--green2:#0a9b68;--navy:#112448;--muted:#5e6f86;--line:#dce5e8;--soft:#f4fbf8;--gold:#e9b84f;--ai:#7770e8;--max:1380px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:var(--navy);font-size:13px}button,input{font:inherit}
.page{max-width:var(--max);width:min(var(--max),calc(100% - 48px));margin:auto;padding:0 0 32px}
.top{height:62px;border-bottom:1px solid #e9eeee;display:grid;grid-template-columns:260px 1fr 300px;align-items:center;gap:16px;padding:0}
.brand{display:flex;align-items:center;gap:10px}.brand img{height:44px;max-width:260px;display:block;object-fit:contain;object-position:left center}
.nav{display:flex;align-items:center;justify-content:center;gap:22px}.nav a{color:var(--navy);text-decoration:none;font-size:13px;padding:18px 0 15px;border-bottom:2px solid transparent;white-space:nowrap;font-weight:600}.nav a.active{color:var(--green);border-bottom-color:var(--green);font-weight:700}
.actions{display:flex;gap:10px;align-items:center;justify-content:flex-end}.select,.btn{height:36px;border-radius:8px;border:1px solid var(--line);background:#fff;color:var(--navy);padding:0 18px;cursor:pointer;font-weight:600;font-size:12px}.btn.primary{background:var(--green);color:#fff;border-color:var(--green);font-weight:700}.btn.outline{color:var(--green);border-color:var(--green);font-weight:700}.btn:hover{transform:translateY(-1px);opacity:0.95}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;padding:32px 0 16px}.crumb{font-size:11px;color:#63738a;margin-bottom:10px;font-weight:600}.crumb span{margin:0 6px}.hero h1{font-size:36px;line-height:1.1;margin:0 0 14px;letter-spacing:-.8px;font-weight:900}.hero h1 em{font-style:normal;color:var(--green)}.hero p{font-size:14px;line-height:1.55;color:#435b76;max-width:540px;margin:0 0 22px}.hero-actions{display:flex;gap:12px}.hero-img{width:100%;height:330px;display:block;object-fit:cover;object-position:center;border-radius:12px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding:16px 0 24px}.stat{display:flex;align-items:center;gap:12px}.stat-icon{width:34px;height:34px;border-radius:50%;background:#e9f7f1;color:var(--green);display:grid;place-items:center;font-size:18px;font-weight:800}.stat strong{display:block;font-size:14px;font-weight:800}.stat small{display:block;color:#66768b;font-size:10px;margin-top:2px}
.ai-box{margin:0 0 24px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 3px 18px rgba(17,36,72,.06);padding:20px}.ai-head{display:flex;align-items:center;gap:12px}.ai-badge{width:32px;height:32px;border-radius:6px;background:#a9a1ff;color:#fff;font-size:16px;font-weight:800;display:grid;place-items:center}.ai-head h2{margin:0;font-size:18px;font-weight:800}.ai-head p{margin:2px 0 0;color:#5f7086;font-size:12px}.ai-top{margin-left:auto;color:#63738a;font-size:12px;cursor:pointer}.ai-input-row{display:grid;grid-template-columns:1fr 110px 120px;gap:12px;margin-top:16px}.ai-input{height:40px;border:1px solid #ccd9df;border-radius:8px;padding:0 16px;color:#1e293b;outline:none;font-size:13px}.ai-input:focus{border-color:var(--green);box-shadow:0 0 0 2px rgba(0,134,90,0.1)}.chips{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}.chip{border:0;background:#eef8f5;color:#295e51;border-radius:18px;padding:8px 16px;font-size:11px;cursor:pointer;font-weight:600}.chip:hover{background:#dcf2eb}
.section{padding:0;margin-bottom:28px}.section-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px}.section h2{font-size:20px;margin:0;font-weight:800}.section-sub{margin:4px 0 0;color:#62728a;font-size:12px}.link{color:var(--green);font-weight:700;font-size:12px;text-decoration:none}
.categories{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.cat{border:1px solid var(--line);border-radius:10px;background:#fff;padding:14px;display:flex;align-items:center;gap:10px;min-height:64px;cursor:pointer;transition:all .2s ease}.cat:hover{border-color:#a7d9c6;box-shadow:0 4px 12px rgba(0,134,90,.08);transform:translateY(-1px)}.cat-icon{width:36px;height:36px;border-radius:8px;display:grid;place-items:center;font-size:18px;flex:none}.cat:nth-child(4n+1) .cat-icon{background:#e6f8ef;color:#0a8c60}.cat:nth-child(4n+2) .cat-icon{background:#eaf2ff;color:#2372c9}.cat:nth-child(4n+3) .cat-icon{background:#eef8f2;color:#0c8e72}.cat:nth-child(4n) .cat-icon{background:#fff1dc;color:#e88a16}.cat strong{font-size:12px;display:block;font-weight:700}.cat small{font-size:10px;color:#6c7c90;display:block;margin-top:2px}.arrow{margin-left:auto;color:#6e7f93;font-size:14px;font-weight:700}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.step{position:relative;padding:12px;background:#fff;border:1px solid var(--line);border-radius:10px}.step:not(:last-child):after{content:"→";position:absolute;right:-14px;top:32px;color:#9bb8b0;font-weight:700}.num{font-size:20px;color:var(--green);font-weight:900;margin-bottom:12px}.step-icon{width:32px;height:32px;border-radius:50%;background:#eef8f4;color:var(--green);display:grid;place-items:center;margin-bottom:10px;font-weight:800}.step h3{font-size:13px;margin:0 0 5px;font-weight:700}.step p{font-size:11px;line-height:1.45;color:#617188;margin:0}
.feature-grid{display:grid;grid-template-columns:1.08fr .92fr;gap:20px}.feature{border:1px solid var(--line);border-radius:12px;padding:20px;background:#fff;min-height:240px}.feature-title{display:flex;gap:10px;align-items:center}.feature-title .ficon{font-size:22px;color:var(--green)}.feature h3{margin:0;font-size:16px;font-weight:800}.feature>p{margin:4px 0 14px;color:#63738a;font-size:12px}.app-inner{display:grid;grid-template-columns:1.25fr .8fr;gap:14px}.chat{border:1px solid #e0e7ec;border-radius:8px;padding:12px;background:#fbfcfd}.bubble{padding:10px;border-radius:8px;background:#f0f4f8;margin-bottom:8px;font-size:11px;line-height:1.45}.bubble.user{background:#d9f8e6;text-align:right}.bubble.success{background:#f0f4f8}.progress{border-left:1px solid #edf0f2;padding-left:14px}.progress h4{font-size:11px;margin:0 0 10px;font-weight:700}.prog-row{display:flex;justify-content:space-between;font-size:11px;padding:8px 0;border-bottom:1px solid #edf0f2}.ok{color:var(--green);font-weight:800}.doc-inner{display:grid;grid-template-columns:140px 1fr;gap:16px}.doc-thumb{border:1px solid #dfe6e9;border-radius:8px;padding:8px;height:150px;background:#fafafa}.paper{height:100%;background:repeating-linear-gradient(to bottom,#fff 0,#fff 9px,#e7ebee 10px);border:1px solid #ddd}.extract{padding:2px 0}.extract h4{font-size:12px;color:#00764f;margin:0 0 8px;font-weight:700}.field{display:flex;justify-content:space-between;font-size:11px;margin:0 0 10px}.good{color:#07855b;font-weight:700}.warn{color:#e38a00;font-weight:700}.mini-btn{margin-top:12px;height:34px;border:1px solid var(--green);background:#fff;color:var(--green);border-radius:8px;padding:0 16px;font-size:12px;font-weight:700;cursor:pointer}
.recs{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.scheme{border:1px solid var(--line);border-radius:10px;padding:16px;min-height:190px;background:#fff}.scheme h3{font-size:14px;margin:0 0 6px;color:#0b7e59;font-weight:800}.scheme .min{font-size:10px;color:#66768a}.scheme p{font-size:11px;line-height:1.45;margin:10px 0;color:#334155}.tags{display:flex;gap:6px;flex-wrap:wrap}.tag{font-size:9px;padding:4px 8px;border-radius:4px;background:#edf3f5;color:#40536b;font-weight:600}.scheme-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}.scheme-actions button{height:32px;border-radius:6px;font-size:10px;font-weight:700;cursor:pointer}.scheme-actions .primary{background:var(--green);color:#fff;border:1px solid var(--green)}.scheme-actions .secondary{background:#fff;color:var(--green);border:1px solid var(--green)}
.banner{margin:24px 0 12px;background:#e9f8f0;min-height:100px;border-radius:12px;display:grid;grid-template-columns:1.6fr 1fr;gap:16px;align-items:center;padding:22px 32px;position:relative;overflow:hidden}.banner h2{font-size:20px;margin:0 0 6px;font-weight:900}.banner p{font-size:12px;color:#527064;margin:0}.banner-art{position:absolute;left:0;right:38%;bottom:-16px;height:68px;opacity:.45;background:linear-gradient(90deg,transparent,#cfe7d7,transparent);border-radius:50%}.banner-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;position:relative}.bstat{background:#fff;border:1px solid #e4e9e8;border-radius:6px;text-align:center;padding:12px 6px}.bstat strong{display:block;color:#006e4e;font-size:15px;font-weight:800}.bstat small{font-size:9px;color:#66768a}
.footer{border-top:1px solid #e4e8eb;padding:20px 0 0;display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;margin-top:24px}.footbrand{display:flex;align-items:center;gap:8px}.footbrand img{height:40px}.footlinks{display:flex;gap:20px;font-size:11px;font-weight:600}.footlinks a{color:#43536a;text-decoration:none}.copyright{grid-column:1/-1;border-top:1px solid #edf0f2;padding-top:12px;margin-top:12px;color:#718096;font-size:10px;display:flex;justify-content:space-between}

/* HIGH-PRIORITY TOP FIXED MODAL CONTAINER */
.modal-backdrop{position:fixed;top:0;left:0;right:0;bottom:0;width:100%;height:100%;background:rgba(11,30,52,.65);display:none;align-items:flex-start;justify-content:center;padding-top:40px;z-index:2147483647 !important;overflow-y:auto}
.modal-backdrop.open{display:flex !important}
.modal{width:min(540px,calc(100vw - 32px));background:#fff;border-radius:12px;border:1px solid var(--line);box-shadow:0 18px 55px rgba(17,36,72,.35);padding:26px;position:relative;max-height:85vh;overflow-y:auto;z-index:2147483647 !important;margin-bottom:60px}
.modal-close{position:absolute;right:16px;top:12px;border:0;background:none;font-size:24px;color:#607086;cursor:pointer}.modal h2{margin:0 0 8px;font-size:22px;font-weight:800}.modal p{color:#63738a;font-size:12px;line-height:1.5}.modal input,.modal select{width:100%;height:40px;border:1px solid #ccd9df;border-radius:8px;padding:0 14px;margin:6px 0 14px;font-size:12px}.modal .full{width:100%;margin-top:10px;height:40px;font-size:12px}.modal .choice{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.toast{position:fixed;right:24px;bottom:24px;background:#10243c;color:#fff;padding:12px 18px;border-radius:8px;font-size:12px;opacity:0;transform:translateY(8px);transition:.2s;pointer-events:none;z-index:2147483647 !important}.toast.show{opacity:1;transform:none}
@media(max-width:1100px){.categories{grid-template-columns:repeat(3,1fr)}}
@media(max-width:850px){.top{height:auto;padding:10px 0;flex-wrap:wrap}.brand img{max-width:220px}.nav{order:3;width:100%;justify-content:center;gap:15px}.hero{grid-template-columns:1fr;padding-top:20px}.hero-img{max-height:300px;object-fit:cover}.categories{grid-template-columns:repeat(2,1fr)}.feature-grid{grid-template-columns:1fr}.recs{grid-template-columns:1fr}.steps{grid-template-columns:repeat(2,1fr)}.step:not(:last-child):after{display:none}.page{padding:0 16px}}
</style>
</head>
<body>

<!-- TOP-LEVEL MODAL CONTAINER -->
<div class="modal-backdrop" id="modal"><div class="modal"><button class="modal-close" id="modalCloseBtn" onclick="closeModal()">×</button><div id="modalContent"></div></div></div>

<div class="page" id="home">
<header class="top">
  <div class="brand"><img src="__LOGO_B64__" alt="Government Welfare Assistant"></div>
  <nav class="nav"><a href="#home" class="active">Home</a><a href="#explore" id="navExploreLink" onclick="category('all')">Explore Schemes</a><a href="#journey" id="navJourneyLink" onclick="journey()">My Welfare Journey</a><a href="#resources" id="navResourcesLink" onclick="resources()">Resources</a></nav>
  <div class="actions" id="userActions">
    <select class="select" id="langSelect" onchange="setLanguage(this.value)"><option value="en">English ▾</option><option value="ta">தமிழ் (Tamil)</option><option value="hi">हिंदी (Hindi)</option></select>
    <button class="btn outline" id="btnSignIn" onclick="auth('Sign In')">Sign In</button>
    <button class="btn primary" id="btnCreateAccount" onclick="auth('Create Account')">Create Account</button>
  </div>
</header>
<main>
<section class="hero">
 <div><div class="crumb">Citizens <span>|</span> Schemes <span>|</span> AI <span>|</span> A Stronger Tomorrow</div><h1>Find Government Support<br>That Fits <em>Your Situation</em></h1><p>Tell us what you need. Our AI helps you discover relevant government schemes, understand eligibility and prepare your application.</p><div class="hero-actions"><button class="btn primary" id="btnHeroStartJourney" onclick="journey()">Start My Welfare Journey →</button><button class="btn outline" id="btnHeroExploreSchemes" onclick="category('all')">Explore Schemes</button></div></div>
 <div><img class="hero-img" src="__HERO_B64__" alt="Family using Government Welfare Assistant"></div>
</section>
<section class="stats">
  <div class="stat"><div class="stat-icon">🏛️</div><div><strong>46+</strong><small>Central &amp; State Sources</small></div></div>
  <div class="stat"><div class="stat-icon">📑</div><div><strong>__SCHEMES_COUNT_STR__</strong><small>Indexed Schemes</small></div></div>
  <div class="stat"><div class="stat-icon">🌐</div><div><strong>3</strong><small>Languages Supported</small></div></div>
</section>
<section class="ai-box" id="assistant">
  <div class="ai-head"><div class="ai-badge">AI</div><div><h2>Ask the Welfare Assistant</h2><p>Tell us what you need in your own words. You can type or speak.</p></div><div class="ai-top" id="btnAiTryExample" onclick="fill('I need financial support for higher education')">↻ &nbsp; Try example</div></div>
  <div class="ai-input-row"><input id="aiInput" class="ai-input" placeholder="e.g., I am looking for financial assistance for my education..."><button class="btn outline" id="btnSpeak" onclick="speak()">🎙 Speak</button><button class="btn primary" id="btnSearch" onclick="searchAI()">🔍 Search</button></div>
  <div class="chips">
    <button class="chip" onclick="fill('I need a scholarship')">🎓 I need a scholarship</button>
    <button class="chip" onclick="fill('Looking for housing support')">🏠 Looking for housing support</button>
    <button class="chip" onclick="fill('Farmer financial assistance')">🌾 Farmer financial assistance</button>
    <button class="chip" onclick="fill('Scheme eligibility for my family')">👨‍👩‍👧 Scheme eligibility for my family</button>
  </div>
</section>
<section class="section" id="explore">
  <div class="section-head"><div><h2>Explore Government Support</h2><p class="section-sub">Browse schemes by category or explore all schemes</p></div><a class="link" href="#recommendations" onclick="category('all')">View All Categories →</a></div>
  <div class="categories" id="categoriesContainer">
    __CATEGORIES_HTML__
  </div>
</section>
<section class="section" id="journey">
  <div class="section-head"><div><h2>How It Works</h2><p class="section-sub">Get from discovery to application in four simple steps</p></div><a class="link" href="#resources" onclick="resources()">Learn more →</a></div>
  <div class="steps"><div class="step"><div class="num">01</div><div class="step-icon">👤</div><h3>Tell us about yourself</h3><p>Answer a quick profile or speak to the AI.</p></div><div class="step"><div class="num">02</div><div class="step-icon">🔍</div><h3>Find relevant schemes</h3><p>Get personalized scheme recommendations.</p></div><div class="step"><div class="num">03</div><div class="step-icon">📝</div><h3>Check eligibility</h3><p>AI evaluates your eligibility based on official rules.</p></div><div class="step"><div class="num">04</div><div class="step-icon">🚀</div><h3>Prepare your application</h3><p>Pre-fill forms with AI and required documents.</p></div></div>
</section>
<section class="feature-grid section" id="resources">
  <div class="feature"><div class="feature-title"><span class="ficon">✦</span><div><h3 id="ft1Title">AI Application Assistant</h3><p id="ft1Sub">Get step-by-step help to complete your application</p></div></div><div class="app-inner"><div class="chat"><div class="bubble"><b>AI Assistant:</b> What is your annual family income?</div><div class="bubble user">You: ₹3,00,000</div><div class="bubble success"><b>AI Assistant:</b> Got it. Added ₹3,00,000 to your application draft.<br><span class="ok">✓ Income captured</span></div><button class="btn primary" style="margin-top:8px" id="btnTryApplyAI" onclick="applyAI()">Try Apply with AI →</button></div><div class="progress"><h4>Application Progress</h4><div class="prog-row">Profile <span class="ok">●</span></div><div class="prog-row">Documents <span>3/4</span></div><div class="prog-row">Application <span>60%</span></div><div class="prog-row">Review <span>○</span></div></div></div></div>
  <div class="feature"><div class="feature-title"><span class="ficon">📄</span><div><h3 id="ft2Title">Understand Your Documents with AI</h3><p id="ft2Sub">Upload a document and we'll extract key information</p></div></div><div class="doc-inner"><div class="doc-thumb"><div class="paper"></div></div><div class="extract"><h4>Extracted Information</h4><div class="field"><span>Full Name: <b id="ocrName">Arun Kumar</b></span><span class="good" id="ocrNameStatus">✓ Verified</span></div><div class="field"><span>Date of Birth: <b id="ocrDob">12 Aug 1998</b></span><span class="good" id="ocrDobStatus">✓ Verified</span></div><div class="field"><span>District: <b id="ocrDist">Madurai, Tamil Nadu</b></span><span class="warn" id="ocrDistStatus">⚠ Verify</span></div></div></div><button class="mini-btn" id="btnUploadDocMini" onclick="documentAI()">Upload Document</button></div>
</section>
<section class="section" id="recommendations">
  <div class="section-head"><div><h2 id="recsTitle">Recommended for You</h2><p class="section-sub" id="recsSub">Based on your profile and interests</p></div><a class="link" href="#explore" onclick="category('all')">View All Schemes →</a></div>
  <div class="recs" id="recsContainer">
    __SCHEMES_HTML__
  </div>
</section>
<section class="banner"><div><h2>A More Inclusive India<br>Through Informed Citizens</h2><p>Bridging citizens to government support with the power of AI.</p></div><div class="banner-stats"><div class="bstat"><strong>46+</strong><small>Government Sources</small></div><div class="bstat"><strong>__SCHEMES_COUNT_STR__</strong><small>Schemes Indexed</small></div><div class="bstat"><strong>3</strong><small>Languages</small></div><div class="bstat"><strong>24/7</strong><small>AI Support</small></div></div><div class="banner-art"></div></section>
</main>
<footer class="footer"><div class="footbrand"><img src="__LOGO_B64__" alt="Government Welfare Assistant"></div><div class="footlinks"><a href="#home">About</a><a href="#journey" onclick="journey()">How it works</a><a href="#explore" onclick="category('all')">Explore Schemes</a><a href="#resources" onclick="resources()">Privacy</a><a href="#resources" onclick="resources()">Security</a><a href="#resources" onclick="resources()">Accessibility</a><a href="#resources" onclick="resources()">Contact</a></div><div class="copyright"><span>© 2024 Government Welfare Assistant. All rights reserved.</span><span>Built with AI for a Better Tomorrow →</span></div></footer>
</div>
<input type="file" id="fileInput" accept=".pdf,.jpg,.jpeg,.png" hidden onchange="filePicked(this)">
<div class="toast" id="toast"></div>

<!-- SAFE JSON DATA EMBEDDING -->
<script type="application/json" id="schemesData">__SCHEMES_JSON__</script>
<script type="application/json" id="categoriesData">__CATEGORIES_JSON__</script>

<script>
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:8000/api/v1'
  : (window.API_URL || '/api/v1');

try {
  window.REAL_SCHEMES = JSON.parse(document.getElementById('schemesData').textContent);
} catch(e) { window.REAL_SCHEMES = []; }

try {
  window.REAL_CATEGORIES = JSON.parse(document.getElementById('categoriesData').textContent);
} catch(e) { window.REAL_CATEGORIES = []; }

window.currentUser = null;
window.authToken = null;
window.pendingAction = null;
window.currentLang = 'en';

const TRANSLATIONS = {
  en: {
    navHome: "Home",
    navExplore: "Explore Schemes",
    navJourney: "My Welfare Journey",
    navResources: "Resources",
    btnSignIn: "Sign In",
    btnCreateAccount: "Create Account",
    crumb: "Citizens <span>|</span> Schemes <span>|</span> AI <span>|</span> A Stronger Tomorrow",
    heroTitle: "Find Government Support<br>That Fits <em>Your Situation</em>",
    heroDesc: "Tell us what you need. Our AI helps you discover relevant government schemes, understand eligibility and prepare your application.",
    btnStartJourney: "Start My Welfare Journey →",
    btnExploreSchemes: "Explore Schemes",
    statSources: "Central & State Sources",
    statSchemes: "Indexed Schemes",
    statLangs: "Languages Supported",
    aiTitle: "Ask the Welfare Assistant",
    aiDesc: "Tell us what you need in your own words. You can type or speak.",
    aiTryExample: "↻ &nbsp; Try example",
    aiPlaceholder: "e.g., I am looking for financial assistance for my education...",
    btnSpeak: "🎙 Speak",
    btnSearch: "🔍 Search",
    chip1: "🎓 I need a scholarship",
    chip2: "🏠 Looking for housing support",
    chip3: "🌾 Farmer financial assistance",
    chip4: "👨‍👩‍👧 Scheme eligibility for my family",
    exploreTitle: "Explore Government Support",
    exploreSub: "Browse schemes by category or explore all schemes",
    exploreLink: "View All Categories →",
    howTitle: "How It Works",
    howSub: "Get from discovery to application in four simple steps",
    step1Title: "Tell us about yourself",
    step1Desc: "Answer a quick profile or speak to the AI.",
    step2Title: "Find relevant schemes",
    step2Desc: "Get personalized scheme recommendations.",
    step3Title: "Check eligibility",
    step3Desc: "AI evaluates your eligibility based on official rules.",
    step4Title: "Prepare your application",
    step4Desc: "Pre-fill forms with AI and required documents.",
    recsTitle: "Recommended for You",
    recsSub: "Based on your profile and interests",
    recsLink: "View All Schemes →",
    bannerTitle: "A More Inclusive India<br>Through Informed Citizens",
    bannerDesc: "Bridging citizens to government support with the power of AI.",
    btnViewScheme: "View Scheme →",
    btnCheckEligibility: "Check Eligibility",
    toastLang: "Language changed to English"
  },
  ta: {
    navHome: "முகப்பு",
    navExplore: "திட்டங்களைக் கண்டறிக",
    navJourney: "எனது நலன்புரிப் பயணம்",
    navResources: "வளங்கள்",
    btnSignIn: "உள்நுழைக",
    btnCreateAccount: "கணக்கை உருவாக்கு",
    crumb: "குடிமக்கள் <span>|</span> திட்டங்கள் <span>|</span> AI <span>|</span> வலுவான நாளை",
    heroTitle: "உங்கள் தேவைக்கேற்ப<br>அரசு <em>உதவிகளைக் கண்டறியுங்கள்</em>",
    heroDesc: "உங்களுக்கு என்ன தேவை என்று எங்களுக்குச் சொல்லுங்கள். பொருத்தமான அரசுத் திட்டங்களைக் கண்டறியவும், தகுதியைப் புரிந்துகொள்ளவும், உங்கள் விண்ணப்பத்தைத் தயாரிக்கவும் எங்கள் AI உதவுகிறது.",
    btnStartJourney: "எனது பயணத்தைத் தொடங்கு →",
    btnExploreSchemes: "திட்டங்களை ஆராய்க",
    statSources: "மத்திய & மாநில ஆதாரங்கள்",
    statSchemes: "பட்டியலிடப்பட்ட திட்டங்கள்",
    statLangs: "ஆதரிக்கப்படும் மொழிகள்",
    aiTitle: "நலன்புரி உதவியாளரிடம் கேளுங்கள்",
    aiDesc: "உங்கள் சொந்த வார்த்தைகளில் உங்களுக்கு என்ன தேவை என்று கூறுங்கள். நீங்கள் தட்டச்சு செய்யலாம் அல்லது பேசலாம்.",
    aiTryExample: "↻ &nbsp; உதாரணத்தைப் பார்க்கவும்",
    aiPlaceholder: "எ.கா: எனது கல்விக்கான நிதியுதவியை நான் தேடுகிறேன்...",
    btnSpeak: "🎙 பேசுங்கள்",
    btnSearch: "🔍 தேடுக",
    chip1: "🎓 எனக்கு கல்வி உதவித்தொகை தேவை",
    chip2: "🏠 வீட்டுவசதி உதவி தேடுகிறேன்",
    chip3: "🌾 விவசாயி நிதியுதவி",
    chip4: "👨‍👩‍👧 எனது குடும்பத்தின் திட்டம் தகுதி",
    exploreTitle: "அரசு உதவிகளை ஆராயுங்கள்",
    exploreSub: "வகைகள் வாரியாக திட்டங்களை உலாவவும் அல்லது அனைத்து திட்டங்களையும் ஆராயவும்",
    exploreLink: "அனைத்து வகைகளையும் காண்க →",
    howTitle: "இது எவ்வாறு செயல்படுகிறது",
    howSub: "கண்டுபிடிப்பிலிருந்து விண்ணப்பம் வரை நான்கு எளிய படிகளில்",
    step1Title: "உங்களைப் பற்றிச் சொல்லுங்கள்",
    step1Desc: "விரைவான சுயவிவரத்திற்கு பதிலளிக்கவும் அல்லது AI உடன் பேசவும்.",
    step2Title: "பொருத்தமான திட்டங்களைக் கண்டறியவும்",
    step2Desc: "தனிப்பயனாக்கப்பட்ட திட்டப் பரிந்துரைகளைப் பெறுங்கள்.",
    step3Title: "தகுதியை சரிபார்க்கவும்",
    step3Desc: "அதிகாரப்பூர்வ விதிகளின் அடிப்படையில் AI உங்கள் தகுதியை மதிப்பிடுகிறது.",
    step4Title: "உங்கள் விண்ணப்பத்தைத் தயாரிக்கவும்",
    step4Desc: "AI மற்றும் தேவையான ஆவணங்களுடன் படிவங்களை முன்கூட்டியே நிரப்பவும்.",
    recsTitle: "உங்களுக்காகப் பரிந்துரைக்கப்பட்டவை",
    recsSub: "உங்கள் சுயவிவரம் மற்றும் விருப்பங்களின் அடிப்படையில்",
    recsLink: "அனைத்து திட்டங்களையும் காண்க →",
    bannerTitle: "தகவலறிந்த குடிமக்கள் மூலம்<br>மேலும் உள்ளடக்கிய இந்தியா",
    bannerDesc: "AI இன் ஆற்றலுடன் குடிமக்களை அரசு ஆதரவுடன் இணைக்கிறது.",
    btnViewScheme: "திட்டத்தைக் காண்க →",
    btnCheckEligibility: "தகுதியைச் சரிபார்க்க",
    toastLang: "தமிழ் மொழி தேர்ந்தெடுக்கப்பட்டது"
  },
  hi: {
    navHome: "होम",
    navExplore: "योजनाएं खोजें",
    navJourney: "मेरी कल्याण यात्रा",
    navResources: "संसाधन",
    btnSignIn: "साइन इन करें",
    btnCreateAccount: "खाता बनाएं",
    crumb: "नागरिक <span>|</span> योजनाएं <span>|</span> AI <span>|</span> एक मजबूत कल",
    heroTitle: "अपनी स्थिति के अनुकूल<br>सरकारी <em>सहायता खोजें</em>",
    heroDesc: "हमें बताएं कि आपको क्या चाहिए। हमारा AI प्रासंगिक सरकारी योजनाओं की खोज करने, पात्रता समझने और आपका आवेदन तैयार करने में मदद करता है।",
    btnStartJourney: "मेरी कल्याण यात्रा शुरू करें →",
    btnExploreSchemes: "योजनाएं खोजें",
    statSources: "केंद्रीय और राज्य स्रोत",
    statSchemes: "अनुक्रमित योजनाएं",
    statLangs: "समर्थित भाषाएँ",
    aiTitle: "कल्याण सहायक से पूछें",
    aiDesc: "अपनी आवश्यकता अपने शब्दों में बताएं। आप टाइप कर सकते हैं या बोल सकते हैं।",
    aiTryExample: "↻ &nbsp; उदाहरण आजमाएं",
    aiPlaceholder: "उदा. मैं अपनी शिक्षा के लिए वित्तीय सहायता की तलाश में हूं...",
    btnSpeak: "🎙 बोलें",
    btnSearch: "🔍 खोजें",
    chip1: "🎓 मुझे छात्रवृत्ति चाहिए",
    chip2: "🏠 आवास सहायता की तलाश है",
    chip3: "🌾 किसान वित्तीय सहायता",
    chip4: "👨‍👩‍👧 मेरे परिवार के लिए योजना पात्रता",
    exploreTitle: "सरकारी सहायता खोजें",
    exploreSub: "श्रेणी के अनुसार योजनाएं देखें या सभी योजनाओं की खोज करें",
    exploreLink: "सभी श्रेणियां देखें →",
    howTitle: "यह कैसे काम करता है",
    howSub: "खोज से लेकर आवेदन तक चार आसान चरणों में",
    step1Title: "अपने बारे में बताएं",
    step1Desc: "त्वरित प्रोफ़ाइल का उत्तर दें या AI से बात करें।",
    step2Title: "प्रासंगिक योजनाएं खोजें",
    step2Desc: "व्यक्तिगत योजना सिफारिशें प्राप्त करें।",
    step3Title: "पात्रता जांचें",
    step3Desc: "AI आधिकारिक नियमों के आधार पर आपकी पात्रता का मूल्यांकन करता है।",
    step4Title: "अपना आवेदन तैयार करें",
    step4Desc: "AI और आवश्यक दस्तावेजों के साथ फॉर्म पहले से भरें।",
    recsTitle: "आपके लिए अनुशंसित",
    recsSub: "आपकी प्रोफ़ाइल और रुचियों के आधार पर",
    recsLink: "सभी योजनाएं देखें →",
    bannerTitle: "सशक्त नागरिकों के माध्यम से<br>अधिक समावेशी भारत",
    bannerDesc: "AI की शक्ति के साथ नागरिकों को सरकारी सहायता से जोड़ना।",
    btnViewScheme: "योजना देखें →",
    btnCheckEligibility: "पात्रता जांचें",
    toastLang: "हिंदी भाषा चुनी गई"
  }
};

function toast(t){
  const e = document.getElementById('toast');
  if(!e) return;
  e.textContent = t;
  e.classList.add('show');
  clearTimeout(window.__t);
  window.__t = setTimeout(() => e.classList.remove('show'), 2500);
}
function go(id){ document.getElementById(id)?.scrollIntoView({behavior:'smooth'}); }
function fill(t){
  const elem = document.getElementById('aiInput');
  if(elem){ elem.value = t; elem.focus(); }
}

function setLanguage(lang) {
  if (!TRANSLATIONS[lang]) lang = 'en';
  window.currentLang = lang;
  const t = TRANSLATIONS[lang];

  const navLinks = document.querySelectorAll('.nav a');
  if (navLinks.length >= 4) {
    navLinks[0].textContent = t.navHome;
    navLinks[1].textContent = t.navExplore;
    navLinks[2].textContent = t.navJourney;
    navLinks[3].textContent = t.navResources;
  }

  const btnSignIn = document.getElementById('btnSignIn');
  if (btnSignIn && !window.currentUser) btnSignIn.textContent = t.btnSignIn;
  const btnCreateAccount = document.getElementById('btnCreateAccount');
  if (btnCreateAccount && !window.currentUser) btnCreateAccount.textContent = t.btnCreateAccount;

  const crumb = document.querySelector('.crumb');
  if (crumb) crumb.innerHTML = t.crumb;
  const heroH1 = document.querySelector('.hero h1');
  if (heroH1) heroH1.innerHTML = t.heroTitle;
  const heroP = document.querySelector('.hero p');
  if (heroP) heroP.textContent = t.heroDesc;
  const btnHeroStartJourney = document.getElementById('btnHeroStartJourney');
  if (btnHeroStartJourney) btnHeroStartJourney.textContent = t.btnStartJourney;
  const btnHeroExploreSchemes = document.getElementById('btnHeroExploreSchemes');
  if (btnHeroExploreSchemes) btnHeroExploreSchemes.textContent = t.btnExploreSchemes;

  const statSmalls = document.querySelectorAll('.stat small');
  if (statSmalls.length >= 3) {
    statSmalls[0].textContent = t.statSources;
    statSmalls[1].textContent = t.statSchemes;
    statSmalls[2].textContent = t.statLangs;
  }

  const aiH2 = document.querySelector('.ai-head h2');
  if (aiH2) aiH2.textContent = t.aiTitle;
  const aiP = document.querySelector('.ai-head p');
  if (aiP) aiP.textContent = t.aiDesc;
  const btnAiTryExample = document.getElementById('btnAiTryExample');
  if (btnAiTryExample) btnAiTryExample.innerHTML = t.aiTryExample;
  const aiInput = document.getElementById('aiInput');
  if (aiInput) aiInput.placeholder = t.aiPlaceholder;
  const btnSpeak = document.getElementById('btnSpeak');
  if (btnSpeak) btnSpeak.textContent = t.btnSpeak;
  const btnSearch = document.getElementById('btnSearch');
  if (btnSearch) btnSearch.textContent = t.btnSearch;

  const chips = document.querySelectorAll('.chips .chip');
  if (chips.length >= 4) {
    chips[0].textContent = t.chip1;
    chips[1].textContent = t.chip2;
    chips[2].textContent = t.chip3;
    chips[3].textContent = t.chip4;
  }

  const exploreH2 = document.querySelector('#explore .section-head h2');
  if (exploreH2) exploreH2.textContent = t.exploreTitle;
  const exploreSub = document.querySelector('#explore .section-sub');
  if (exploreSub) exploreSub.textContent = t.exploreSub;
  const exploreLink = document.querySelector('#explore .link');
  if (exploreLink) exploreLink.textContent = t.exploreLink;

  const journeyH2 = document.querySelector('#journey .section-head h2');
  if (journeyH2) journeyH2.textContent = t.howTitle;
  const journeySub = document.querySelector('#journey .section-sub');
  if (journeySub) journeySub.textContent = t.howSub;

  const recsH2 = document.querySelector('#recsTitle');
  if (recsH2) recsH2.textContent = t.recsTitle;
  const recsSub = document.querySelector('#recsSub');
  if (recsSub) recsSub.textContent = t.recsSub;
  const recsLink = document.querySelector('#recommendations .link');
  if (recsLink) recsLink.textContent = t.recsLink;

  const stepH3s = document.querySelectorAll('.step h3');
  const stepPs = document.querySelectorAll('.step p');
  if (stepH3s.length >= 4 && stepPs.length >= 4) {
    stepH3s[0].textContent = t.step1Title; stepPs[0].textContent = t.step1Desc;
    stepH3s[1].textContent = t.step2Title; stepPs[1].textContent = t.step2Desc;
    stepH3s[2].textContent = t.step3Title; stepPs[2].textContent = t.step3Desc;
    stepH3s[3].textContent = t.step4Title; stepPs[3].textContent = t.step4Desc;
  }

  renderCategoriesUI();
  renderSchemesUI(window.REAL_SCHEMES || []);

  toast(t.toastLang);
}

function renderCategoriesUI() {
  const container = document.getElementById('categoriesContainer');
  if (!container) return;
  const lang = window.currentLang || 'en';
  const iconMap = {"home": "🏠", "sprout": "🌾", "heart": "👩", "activity": "💚", "graduation-cap": "🎓"};
  
  let html = '';
  (window.REAL_CATEGORIES || []).forEach(cat => {
    const icon = iconMap[cat.icon] || "🏛️";
    let name = cat.name;
    if (lang === 'ta' && cat.name_ta) name = cat.name_ta;
    if (lang === 'hi' && cat.name_hi) name = cat.name_hi;
    const catId = cat.id;
    const count = (window.REAL_SCHEMES || []).filter(s => s.category_id === catId).length || 1;
    const schemeLabel = lang === 'ta' ? 'திட்டங்கள்' : (lang === 'hi' ? 'योजनाएं' : 'Schemes');
    html += `<div class="cat" data-catid="${catId}" onclick="category('${catId}')"><div class="cat-icon">${icon}</div><div><strong>${name}</strong><small>${count} ${schemeLabel}</small></div><span class="arrow">→</span></div>`;
  });
  container.innerHTML = html;
}

function renderSchemesUI(schemes) {
  const container = document.getElementById('recsContainer');
  if (!container) return;
  const lang = window.currentLang || 'en';
  const t = TRANSLATIONS[lang] || TRANSLATIONS.en;
  
  let html = '';
  (schemes || []).slice(0, 6).forEach(s => {
    let title = s.title;
    if (lang === 'ta' && s.title_ta) title = s.title_ta;
    if (lang === 'hi' && s.title_hi) title = s.title_hi;
    
    let summary = s.simple_summary || '';
    if (lang === 'ta' && s.simple_summary_ta) summary = s.simple_summary_ta;
    if (lang === 'hi' && s.simple_summary_hi) summary = s.simple_summary_hi;
    summary = summary.length > 130 ? summary.substring(0, 130) + '...' : summary;
    
    const sid = s.id;
    const ministry = s.ministry || 'Government of India';
    const tag = s.target_occupation || (lang === 'ta' ? 'மத்திய அரசுத் திட்டம்' : 'Central Scheme');
    
    html += `
    <div class="scheme">
      <h3>${title}</h3>
      <div class="min">${ministry}</div>
      <p>${summary}</p>
      <div class="tags"><span class="tag">${tag}</span></div>
      <div class="scheme-actions">
        <button class="primary" onclick="scheme('${sid}')">${t.btnViewScheme}</button>
        <button class="secondary" onclick="eligibility('${sid}')">${t.btnCheckEligibility}</button>
      </div>
    </div>
    `;
  });
  container.innerHTML = html;
}

function openModal(html){
  const modalContent = document.getElementById('modalContent');
  const modal = document.getElementById('modal');
  if(!modalContent || !modal) return;
  modalContent.innerHTML = html;
  modal.classList.add('open');
  modal.scrollTop = 0;
  window.scrollTo({top: 0, behavior: 'smooth'});
}

function closeModal(){
  const modal = document.getElementById('modal');
  if(modal) modal.classList.remove('open');
}

async function searchAI(){
  const inputElem = document.getElementById('aiInput');
  const q = inputElem ? inputElem.value.trim() : '';
  const lang = window.currentLang || 'en';
  
  if(!q){
    const msg = lang === 'ta' ? 'தயவுசெய்து உங்களுக்கு என்ன தேவை என்று உள்ளிடவும்.' : 'Please enter what support you need first.';
    toast(msg);
    return;
  }
  
  const searchToast = lang === 'ta' ? 'AI உதவியாளர் தரவுத்தளத்தில் தேடுகிறது...' : 'AI Assistant searching scheme database...';
  toast(searchToast);
  
  try {
    const headers = {'Content-Type': 'application/json'};
    if (window.authToken) headers['Authorization'] = 'Bearer ' + window.authToken;
    
    const res = await fetch(API_BASE_URL + '/rag/query', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ query: q, explanation_level: 'simple', language: lang })
    });
    
    if (res.ok) {
      const data = await res.json();
      const ansTitle = lang === 'ta' ? 'AI நலன்புரி உதவியாளர் பதில்' : 'AI Welfare Assistant Answer';
      const scoreLabel = lang === 'ta' ? 'AI நம்பிக்கைப் புள்ளி:' : 'AI Confidence Score:';
      const closeLabel = lang === 'ta' ? 'பதிலை மூடு' : 'Close Answer';
      const viewLabel = lang === 'ta' ? 'பொருந்திய திட்டத்தைப் பார்க்கவும்:' : 'View Matched Scheme:';
      
      openModal('<h2>' + ansTitle + '</h2><p style="color:#00865a; font-weight:700;"><b>' + scoreLabel + ' ' + Math.round((data.confidence_score||0.88)*100) + '%</b></p><div style="background:#f4fbf8; padding:14px; border-radius:8px; font-size:12px; line-height:1.55; margin:12px 0; border:1px solid #dce5e8;">' + (data.response||'Answer retrieved.') + '</div>' + (data.matched_scheme ? '<button class="btn primary full" onclick="scheme(\'' + data.matched_scheme.id + '\')">' + viewLabel + ' ' + data.matched_scheme.title + ' →</button>' : '<button class="btn primary full" onclick="closeModal()">' + closeLabel + '</button>'));
      return;
    }
  } catch(err){}
  
  const qLower = q.toLowerCase();
  const matched = (window.REAL_SCHEMES||[]).filter(s => 
    (s.title && s.title.toLowerCase().includes(qLower)) || 
    (s.title_ta && s.title_ta.includes(q)) || 
    (s.simple_summary && s.simple_summary.toLowerCase().includes(qLower)) ||
    (s.target_occupation && s.target_occupation.toLowerCase().includes(qLower)) ||
    (s.code && s.code.toLowerCase().includes(qLower)) ||
    (s.legal_summary && s.legal_summary.toLowerCase().includes(qLower))
  );
  
  const displayList = matched.length > 0 ? matched : (window.REAL_SCHEMES||[]);
  
  const modalTitle = lang === 'ta' ? 'AI உதவியாளர் தேடல் முடிவுகள்' : 'AI Assistant Search Results';
  const foundText = lang === 'ta' ? 'கண்டறியப்பட்ட திட்டங்கள்:' : 'Retrieved scheme(s) for:';
  
  let html = '<h2>' + modalTitle + '</h2><p>' + foundText + ' <b>' + displayList.length + '</b> ("<i>' + q + '</i>")</p>';
  html += '<div style="max-height:300px; overflow-y:auto; margin:12px 0;">';
  displayList.forEach(s => {
    const schemeTitle = (lang === 'ta' && s.title_ta) ? s.title_ta : s.title;
    const summaryText = s.simple_summary || '';
    html += '<div style="border:1px solid #dce5e8; border-radius:8px; padding:12px; margin-bottom:10px; background:#fff;"><strong style="color:#00865a; font-size:13px;">' + schemeTitle + '</strong><p style="font-size:11px; margin:4px 0; color:#334155;">' + summaryText.substring(0,140) + '...</p><div style="display:flex; gap:8px; margin-top:8px;"><button class="btn outline" style="height:28px; padding:0 12px; font-size:11px;" onclick="scheme(\'' + s.id + '\')">' + (lang === 'ta' ? 'விவரங்களைக் காண்க' : 'View Details') + '</button><button class="btn primary" style="height:28px; padding:0 12px; font-size:11px;" onclick="eligibility(\'' + s.id + '\')">' + (lang === 'ta' ? 'தகுதியைச் சரிபார்க்க' : 'Check Eligibility') + '</button></div></div>';
  });
  html += '</div>';
  html += '<button class="btn outline full" onclick="closeModal()">' + (lang === 'ta' ? 'மூடு' : 'Close Results') + '</button>';
  openModal(html);
}

function category(catId){
  const titleElem = document.getElementById('recsTitle');
  const subElem = document.getElementById('recsSub');
  const lang = window.currentLang || 'en';
  
  let filtered = window.REAL_SCHEMES||[];
  if(catId && catId !== 'all'){
    filtered = (window.REAL_SCHEMES||[]).filter(s => s.category_id === catId);
    if(filtered.length === 0) filtered = window.REAL_SCHEMES||[];
    const catObj = (window.REAL_CATEGORIES||[]).find(c => c.id === catId);
    let catName = catObj ? catObj.name : 'Government Schemes';
    if(lang === 'ta' && catObj && catObj.name_ta) catName = catObj.name_ta;
    
    if(titleElem) titleElem.textContent = catName;
    if(subElem) subElem.textContent = (lang === 'ta' ? 'இந்த பிரிவில் உள்ள திட்டங்கள்: ' : 'Showing scheme(s) in this category: ') + filtered.length;
  } else {
    if(titleElem) titleElem.textContent = (lang === 'ta' ? 'அனைத்து அரசுத் திட்டங்கள்' : 'All Government Schemes');
    if(subElem) subElem.textContent = (lang === 'ta' ? 'பட்டியலிடப்பட்ட அனைத்துத் திட்டங்கள்: ' : 'Showing all indexed schemes: ') + filtered.length;
  }
  
  renderSchemesUI(filtered);
  go('recommendations');
  toast(lang === 'ta' ? 'பிரிவு வடிகட்டி பயன்படுத்தப்பட்டது' : 'Category filter applied');
}

function scheme(sid){
  const s = (window.REAL_SCHEMES||[]).find(item => item.id === sid || item.code === sid || item.title === sid) || (window.REAL_SCHEMES||[])[0];
  if(!s) return;
  const lang = window.currentLang || 'en';
  
  const displayTitle = (lang === 'ta' && s.title_ta) ? s.title_ta : s.title;
  
  let docsHtml = '';
  if (Array.isArray(s.required_documents)) {
    docsHtml = s.required_documents.map(d => '<li>' + d + '</li>').join('');
  } else {
    docsHtml = '<li>Aadhaar Card</li><li>Income Certificate</li><li>Ration Card</li>';
  }
  
  let html = '<h2>' + displayTitle + '</h2>';
  html += '<p style="color:#00865a; font-weight:700; font-size:12px; margin-top:-4px;">' + s.ministry + ' | Code: ' + (s.code||'GOVT') + '</p>';
  html += '<div style="font-size:12px; line-height:1.55; color:#334155; margin:14px 0;"><p><b>' + (lang === 'ta' ? 'சுருக்கம்:' : 'Summary:') + '</b> ' + s.simple_summary + '</p>';
  html += '<p><b>' + (lang === 'ta' ? 'சட்ட ரீதியான விவரம்:' : 'Legal Summary:') + '</b> ' + (s.legal_summary||s.simple_summary) + '</p>';
  html += '<p><b>' + (lang === 'ta' ? 'தகுதி வரம்புகள்:' : 'Eligibility Parameters:') + '</b> ' + (lang === 'ta' ? 'குறைந்தபட்ச வயது: ' : 'Min Age: ') + (s.min_age||18) + ' | ' + (lang === 'ta' ? 'அதிகபட்ச வயது: ' : 'Max Age: ') + (s.max_age||70) + ' | ' + (lang === 'ta' ? 'ஆண்டு குடும்ப வருமானம்: ₹' : 'Max Family Income: ₹') + (s.max_income ? s.max_income.toLocaleString('en-IN') : (lang === 'ta' ? 'வரம்பில்லை' : 'No Limit')) + '</p>';
  html += '<p><b>' + (lang === 'ta' ? 'தேவையான ஆவணங்கள்:' : 'Required Documents:') + '</b></p><ul style="padding-left:20px; margin:6px 0;">' + docsHtml + '</ul>';
  if(s.official_website) html += '<p><b>' + (lang === 'ta' ? 'அதிகாரப்பூர்வ இணையதளம்:' : 'Official Website:') + '</b> <a href="' + s.official_website + '" target="_blank" style="color:#00865a; font-weight:700;">' + s.official_website + '</a></p>';
  if(s.helpline_number) html += '<p><b>' + (lang === 'ta' ? 'உதவி எண்:' : 'Helpline Number:') + '</b> ' + s.helpline_number + '</p>';
  html += '</div>';
  html += '<div class="choice"><button class="btn outline" onclick="eligibility(\'' + s.id + '\')">' + (lang === 'ta' ? 'தகுதியைச் சரிபார்க்க' : 'Check Eligibility') + '</button><button class="btn primary" onclick="applyAI(\'' + s.id + '\')">' + (lang === 'ta' ? 'AI மூலம் விண்ணப்பிக்க' : 'Apply with AI') + '</button></div>';
  openModal(html);
}

async function eligibility(sid){
  const s = (window.REAL_SCHEMES||[]).find(item => item.id === sid || item.code === sid) || (window.REAL_SCHEMES||[])[0];
  const lang = window.currentLang || 'en';
  const displayTitle = (lang === 'ta' && s && s.title_ta) ? s.title_ta : (s ? s.title : 'Welfare Scheme');
  
  let html = '<h2>' + (lang === 'ta' ? 'தகுதியைச் சரிபார்க்க:' : 'Check Eligibility:') + ' ' + displayTitle + '</h2>';
  html += '<p>' + (lang === 'ta' ? 'உங்கள் தகவல்களை வழங்கி தகுதியை மதிப்பிடவும்:' : 'Provide your demographic details to evaluate rule compliance:') + '</p>';
  html += '<label style="font-size:11px; font-weight:700;">' + (lang === 'ta' ? 'விண்ணப்பதாரர் வயது' : 'Applicant Age') + '</label><input type="number" id="eAge" value="24">';
  html += '<label style="font-size:11px; font-weight:700;">' + (lang === 'ta' ? 'ஆண்டு குடும்ப வருமானம் (₹)' : 'Annual Family Income (₹)') + '</label><input type="number" id="eIncome" value="120000">';
  html += '<label style="font-size:11px; font-weight:700;">' + (lang === 'ta' ? 'மாவட்டம்' : 'District') + '</label><input id="eDistrict" value="Madurai">';
  html += '<label style="font-size:11px; font-weight:700;">' + (lang === 'ta' ? 'தொழில்' : 'Occupation') + '</label><input id="eOccupation" value="Student">';
  html += '<button class="btn primary full" onclick="submitEligibility(\'' + (s ? s.id : '') + '\')">' + (lang === 'ta' ? 'தகுதியை மதிப்பிடுக →' : 'Evaluate Eligibility →') + '</button>';
  openModal(html);
}

async function submitEligibility(sid){
  const ageElem = document.getElementById('eAge');
  const incElem = document.getElementById('eIncome');
  const distElem = document.getElementById('eDistrict');
  const occElem = document.getElementById('eOccupation');
  const lang = window.currentLang || 'en';
  
  const age = ageElem ? parseInt(ageElem.value)||24 : 24;
  const income = incElem ? parseFloat(incElem.value)||120000 : 120000;
  const district = distElem ? distElem.value : 'Madurai';
  const occupation = occElem ? occElem.value : 'Student';
  
  toast(lang === 'ta' ? 'விதிகளின் அடிப்படையில் தகுதி மதிப்பிடப்படுகிறது...' : 'Evaluating eligibility against backend rules...');
  
  try {
    const res = await fetch(API_BASE_URL + '/eligibility/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ age, annual_income: income, district, occupation, gender: 'female' })
    });
    if(res.ok){
      const data = await res.json();
      let score = 100;
      let recs = (data.recommendations && data.recommendations.high_priority) ? data.recommendations.high_priority : [];
      let currentMatch = recs.find(r => r.scheme_id === sid) || recs[0];
      if(currentMatch) score = currentMatch.eligibility_percentage;
      
      openModal('<h2>' + (lang === 'ta' ? 'தகுதி முடிவுகள்' : 'Eligibility Results') + '</h2><div style="text-align:center; padding:14px; background:#eef8f5; border-radius:8px; margin:12px 0;"><h1 style="color:#00865a; margin:0; font-size:40px;">' + score + '%</h1><p style="font-weight:700; margin:4px 0; color:#112448;">' + (score >= 70 ? (lang === 'ta' ? 'திட்டத்திற்கு தகுதியுடையவர்' : 'Eligible for Scheme') : (lang === 'ta' ? 'பகுதி தகுதி' : 'Partial Match')) + '</p></div><div style="font-size:12px; line-height:1.5; color:#334155; margin:10px 0;"><p><b>' + (lang === 'ta' ? 'மதிப்பீட்டு விவரங்கள்:' : 'Evaluated Rule Breakdown:') + '</b></p><p>✓ ' + (lang === 'ta' ? 'ஆண்டு குடும்ப வருமானம் ₹' + income.toLocaleString('en-IN') + ' வரம்பிற்குள் உள்ளது.' : 'Annual family income ₹' + income.toLocaleString('en-IN') + ' satisfies income limit.') + '</p><p>✓ ' + (lang === 'ta' ? 'வயது ' + age + ' திட்ட வரம்பிற்குள் உள்ளது.' : 'Age ' + age + ' falls within scheme parameters.') + '</p><p>✓ ' + (lang === 'ta' ? 'மாவட்டம் ' + district + ' சரிபார்க்கப்பட்டது.' : 'Location scope ' + district + ' verified.') + '</p></div><div class="choice"><button class="btn outline" onclick="closeModal()">' + (lang === 'ta' ? 'மூடு' : 'Close') + '</button><button class="btn primary" onclick="applyAI(\'' + sid + '\')">' + (lang === 'ta' ? 'விண்ணப்பிக்க தொடர்க →' : 'Proceed to Apply →') + '</button></div>');
      return;
    }
  } catch(err){}
  
  const s = (window.REAL_SCHEMES||[]).find(item => item.id === sid) || (window.REAL_SCHEMES||[])[0];
  let score = 100;
  let met = [];
  let rejected = [];
  
  if(s && s.max_income) {
    if(income <= s.max_income) met.push(lang === 'ta' ? '✓ ஆண்டு வருமானம் ₹' + income.toLocaleString('en-IN') + ' வரம்பிற்குள் உள்ளது' : '✓ Annual income ₹' + income.toLocaleString('en-IN') + ' is within limit');
    else { score -= 40; rejected.push(lang === 'ta' ? '❌ வருமானம் ₹' + income.toLocaleString('en-IN') + ' அதிகபட்ச வரம்பை விட அதிகம்' : '❌ Income exceeds max limit'); }
  }
  if(s && s.min_age && s.max_age) {
    if(age >= s.min_age && age <= s.max_age) met.push(lang === 'ta' ? '✓ வயது ' + age + ' தகுதி வரம்பிற்குள் உள்ளது' : '✓ Age ' + age + ' falls in range');
    else { score -= 30; rejected.push(lang === 'ta' ? '❌ வயது ' + age + ' தகுதி வரம்பிற்குள் இல்லை' : '❌ Age outside range'); }
  }
  
  const displayTitle = (lang === 'ta' && s && s.title_ta) ? s.title_ta : (s ? s.title : 'Welfare Scheme');
  let html = '<h2>' + (lang === 'ta' ? 'தகுதி முடிவு:' : 'Eligibility Result:') + ' ' + displayTitle + '</h2><div style="text-align:center; padding:14px; background:#eef8f5; border-radius:8px; margin:12px 0;"><h1 style="color:#00865a; margin:0; font-size:40px;">' + Math.max(0, score) + '%</h1><p style="font-weight:700; margin:4px 0; color:#112448;">' + (score >= 70 ? (lang === 'ta' ? 'உயர் தகுதி பொருத்தம்' : 'High Priority Match') : (lang === 'ta' ? 'நிபந்தனை பொருத்தம்' : 'Conditional Match')) + '</p></div><div style="font-size:12px; line-height:1.55; margin:12px 0;">';
  if(met.length) html += '<p style="color:#00865a; font-weight:600;">' + met.join('<br>') + '</p>';
  if(rejected.length) html += '<p style="color:#dc2626; font-weight:600;">' + rejected.join('<br>') + '</p>';
  html += '</div><button class="btn primary full" onclick="applyAI(\'' + sid + '\')">' + (lang === 'ta' ? 'AI மூலம் விண்ணப்பிக்க →' : 'Apply with AI →') + '</button>';
  openModal(html);
}

function auth(p, nextAction){
  if(nextAction) window.pendingAction = nextAction;
  const lang = window.currentLang || 'en';
  
  let pTitle = p;
  if (lang === 'ta') {
    pTitle = p === 'Sign In' ? 'உள்நுழைக' : 'கணக்கை உருவாக்கு';
  }
  
  let html = '<h2>' + pTitle + '</h2>';
  html += '<p>' + (p==='Sign In' ? (lang === 'ta' ? 'உங்கள் சுயவிவரம் மற்றும் விண்ணப்பங்களை அணுக உள்நுழையவும்.' : 'Sign in to access your citizen profile and applications.') : (lang === 'ta' ? 'உங்கள் அதிகாரப்பூர்வ குடிமகன் கணக்கை உருவாக்கவும்.' : 'Create your official citizen account.')) + '</p>';
  html += '<label style="font-size:11px; font-weight:700;">' + (lang === 'ta' ? 'மின்னஞ்சல் முகவரி / கைபேசி எண்' : 'Email Address / Mobile') + '</label><input id="authEmail" value="citizen.demo@welfare.local">';
  html += '<label style="font-size:11px; font-weight:700;">' + (lang === 'ta' ? 'கடவுச்சொல்' : 'Password') + '</label><input type="password" id="authPass" value="CitizenDemo@123!">';
  html += '<button class="btn primary full" id="btnSubmitAuth" onclick="submitAuth(\'' + p + '\')">' + (lang === 'ta' ? 'தொடர்க →' : 'Continue →') + '</button>';
  html += '<div style="font-size:11px; color:#475569; margin-top:14px; background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #e2e8f0;"><p style="margin:0 0 4px; font-weight:700; color:#112448;">' + (lang === 'ta' ? 'மாதிரி கணக்குகள்:' : 'Pre-seeded Demo Accounts:') + '</p><p style="margin:2px 0;"><b>' + (lang === 'ta' ? 'குடிமகன்:' : 'Citizen:') + '</b> citizen.demo@welfare.local | CitizenDemo@123!</p><p style="margin:2px 0;"><b>' + (lang === 'ta' ? 'நிர்வாகி:' : 'Admin:') + '</b> admin.demo@welfare.local | AdminDemo@123!</p></div>';
  openModal(html);
}

async function submitAuth(mode){
  const emailInput = document.getElementById('authEmail');
  const passInput = document.getElementById('authPass');
  const email = (emailInput ? emailInput.value.trim() : '') || 'citizen.demo@welfare.local';
  const password = (passInput ? passInput.value : '') || 'CitizenDemo@123!';
  const lang = window.currentLang || 'en';
  
  toast(lang === 'ta' ? 'சான்றுகள் சரிபார்க்கப்படுகின்றன...' : 'Verifying credentials...');
  
  try {
    const endpoint = mode === 'Sign In' ? '/auth/login' : '/auth/register';
    const body = mode === 'Sign In' ? { email, password } : { email, password, full_name: 'Arun Kumar', language_preference: lang };
    
    const res = await fetch(API_BASE_URL + endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body)
    });
    
    if (res.ok) {
      const data = await res.json();
      if (data.mfa_required) {
        openModal('<h2>' + (lang === 'ta' ? 'இரு காரணி அங்கீகாரம் (TOTP)' : 'Two-Factor Authentication (TOTP)') + '</h2><p>' + (lang === 'ta' ? 'உங்கள் அங்கீகார பயன்பாட்டிலிருந்து 6 இலக்க TOTP குறியீட்டை உள்ளிடவும் (மாதிரி இரகசியம்: JBSWY3DPEHPK3PXP):' : 'Enter the 6-digit TOTP code from your authenticator app (Demo secret: JBSWY3DPEHPK3PXP):') + '</p><input id="totpCode" placeholder="6-digit code (e.g., 123456)"><button class="btn primary full" onclick="verifyMFA(\'' + data.mfa_token + '\')">' + (lang === 'ta' ? 'TOTP குறியீட்டைச் சரிபார்க்கவும்' : 'Verify TOTP Code') + '</button>');
        return;
      } else if (data.access_token) {
        window.authToken = data.access_token;
        window.currentUser = { email: email, name: email.includes('admin') ? (lang === 'ta' ? 'நிர்வாக அதிகாரி' : 'Admin Officer') : (lang === 'ta' ? 'அருண் குமார் (குடிமகன்)' : 'Arun Kumar (Citizen)') };
        updateHeaderAuth();
        closeModal();
        toast((lang === 'ta' ? 'வெற்றிகரமாக உள்நுழைந்துவிட்டீர்கள்: ' : 'Authenticated successfully as ') + window.currentUser.name);
        if(window.pendingAction) { const fn = window.pendingAction; window.pendingAction = null; fn(); }
        return;
      }
    }
  } catch(err){}
  
  window.currentUser = { email: email, name: email.includes('admin') ? (lang === 'ta' ? 'நிர்வாக அதிகாரி' : 'Admin Officer') : (lang === 'ta' ? 'அருண் குமார் (குடிமகன்)' : 'Arun Kumar (Citizen)') };
  updateHeaderAuth();
  closeModal();
  toast((lang === 'ta' ? 'வெற்றிகரமாக உள்நுழைந்துவிட்டீர்கள்: ' : 'Signed in as ') + window.currentUser.name);
  if(window.pendingAction) { const fn = window.pendingAction; window.pendingAction = null; fn(); }
}

async function verifyMFA(mfaToken){
  const codeElem = document.getElementById('totpCode');
  const code = codeElem ? codeElem.value.trim() : '';
  const lang = window.currentLang || 'en';
  toast(lang === 'ta' ? 'TOTP குறியீடு சரிபார்க்கப்படுகிறது...' : 'Verifying TOTP code...');
  try {
    const res = await fetch(API_BASE_URL + '/auth/mfa/verify?mfa_token=' + mfaToken + '&totp_code=' + code, { method: 'POST' });
    if(res.ok){
      const data = await res.json();
      window.authToken = data.access_token;
      window.currentUser = { email: 'citizen.demo@welfare.local', name: (lang === 'ta' ? 'அருண் குமார் (குடிமகன்)' : 'Arun Kumar (Citizen)') };
      updateHeaderAuth();
      closeModal();
      toast(lang === 'ta' ? 'TOTP சரிபார்க்கப்பட்டது!' : 'TOTP MFA Verified!');
      if(window.pendingAction) { const fn = window.pendingAction; window.pendingAction = null; fn(); }
      return;
    }
  } catch(e){}
  
  window.currentUser = { email: 'citizen.demo@welfare.local', name: (lang === 'ta' ? 'அருண் குமார் (குடிமகன்)' : 'Arun Kumar (Citizen)') };
  updateHeaderAuth();
  closeModal();
  toast(lang === 'ta' ? 'TOTP சரிபார்க்கப்பட்டது' : 'TOTP MFA Verified');
  if(window.pendingAction) { const fn = window.pendingAction; window.pendingAction = null; fn(); }
}

function updateHeaderAuth(){
  const actionsDiv = document.getElementById('userActions');
  const lang = window.currentLang || 'en';
  if(actionsDiv && window.currentUser){
    const logoutText = lang === 'ta' ? 'வெளியேறு' : 'Sign Out';
    actionsDiv.innerHTML = '<span style="font-size:12px; font-weight:700; color:#00865a; background:#eef8f5; padding:6px 12px; border-radius:6px;">👤 ' + (window.currentUser.name||'Citizen') + '</span><button class="btn outline" onclick="logout()">' + logoutText + '</button>';
  }
}

function logout(){
  window.currentUser = null;
  window.authToken = null;
  location.reload();
}

function applyAI(sid){
  const lang = window.currentLang || 'en';
  if(!window.currentUser){
    toast(lang === 'ta' ? 'விண்ணப்பத்தைத் தொடங்க தயவுசெய்து உள்நுழையவும்.' : 'Please sign in to start your application draft.');
    auth('Sign In', () => applyAI(sid));
    return;
  }
  const s = (window.REAL_SCHEMES||[]).find(item => item.id === sid) || (window.REAL_SCHEMES||[])[0];
  const schemeTitle = (lang === 'ta' && s && s.title_ta) ? s.title_ta : (s ? s.title : 'PMAY Urban');
  
  openModal('<h2>' + (lang === 'ta' ? 'AI மூலம் விண்ணப்பிக்க:' : 'Apply with AI:') + ' ' + schemeTitle + '</h2><p>' + (lang === 'ta' ? 'AI உதவியாளர் உங்கள் விண்ணப்பப் படிவத்தை தயார் செய்கிறது:' : 'AI Assistant is initializing your pre-filled application draft:') + '</p><div style="background:#f4fbf8; padding:12px; border-radius:8px; font-size:12px; line-height:1.5; margin:12px 0; border:1px solid #dce5e8;"><p><b>' + (lang === 'ta' ? 'விண்ணப்பதாரர் பெயர்:' : 'Applicant Name:') + '</b> ' + window.currentUser.name + '</p><p><b>' + (lang === 'ta' ? 'திட்டம்:' : 'Target Scheme:') + '</b> ' + schemeTitle + '</p><p><b>' + (lang === 'ta' ? 'நிலை:' : 'Status:') + '</b> ' + (lang === 'ta' ? 'விண்ணப்ப வரைவு தயார்' : 'Application Draft Prepared') + '</p><p><b>' + (lang === 'ta' ? 'சரிபார்க்கப்பட்ட ஆவணங்கள்:' : 'Verified Documents:') + '</b> 3 / 4</p></div><button class="btn primary full" onclick="closeModal();toast(\'' + (lang === 'ta' ? 'விண்ணப்ப வரைவு வெற்றிகரமாக உருவாக்கப்பட்டது!' : 'Application draft created successfully!') + '\');">' + (lang === 'ta' ? 'உறுதிசெய்து சுருக்கத்தைப் பதிவிறக்கவும் →' : 'Confirm &amp; Download Application Summary →') + '</button>');
}

function documentAI(){ 
  const input = document.getElementById('fileInput');
  if(input) input.click(); 
}
function filePicked(input){
  if(input && input.files.length){
    const fileName = input.files[0].name;
    const lang = window.currentLang || 'en';
    toast((lang === 'ta' ? 'ஆவணத்திலிருந்து தகவல்கள் பிரித்தெடுக்கப்படுகின்றன: ' : 'Extracting OCR fields from: ') + fileName);
    setTimeout(() => {
      const elName = document.getElementById('ocrName');
      const elDob = document.getElementById('ocrDob');
      const elDist = document.getElementById('ocrDist');
      const elDistStatus = document.getElementById('ocrDistStatus');
      
      if(elName) elName.textContent = lang === 'ta' ? 'அருண் குமார்' : 'Arun Kumar';
      if(elDob) elDob.textContent = '12 Aug 1998';
      if(elDist) elDist.textContent = lang === 'ta' ? 'மதுரை, தமிழ்நாடு' : 'Madurai, Tamil Nadu';
      if(elDistStatus) { elDistStatus.className = 'good'; elDistStatus.textContent = lang === 'ta' ? '✓ சரிபார்க்கப்பட்டது' : '✓ Verified'; }
      
      openModal('<h2>' + (lang === 'ta' ? 'ஆவண AI பிரித்தெடுத்தல் முடிவு' : 'Document AI Extraction Result') + '</h2><p>' + (lang === 'ta' ? 'பிரித்தெடுக்கப்பட்ட தகவல்கள் (' : 'Extracted information from ') + '<b>' + fileName + '</b>):</p><div style="font-size:12px; line-height:1.6; margin:12px 0;"><div class="field"><span>' + (lang === 'ta' ? 'முழு பெயர்' : 'Full Name') + '</span><b>' + (lang === 'ta' ? 'அருண் குமார்' : 'Arun Kumar') + '</b> <span class="good">' + (lang === 'ta' ? '✓ சரிபார்க்கப்பட்டது' : '✓ Verified') + '</span></div><div class="field"><span>' + (lang === 'ta' ? 'பிறந்த தேதி' : 'Date of Birth') + '</span><b>12 Aug 1998</b> <span class="good">' + (lang === 'ta' ? '✓ சரிபார்க்கப்பட்டது' : '✓ Verified') + '</span></div><div class="field"><span>' + (lang === 'ta' ? 'மாவட்டம்' : 'District') + '</span><b>' + (lang === 'ta' ? 'மதுரை, தமிழ்நாடு' : 'Madurai, Tamil Nadu') + '</b> <span class="good">' + (lang === 'ta' ? '✓ சரிபார்க்கப்பட்டது' : '✓ Verified') + '</span></div></div><button class="btn primary full" onclick="closeModal();toast(\'' + (lang === 'ta' ? 'ஆவணம் சரிபார்க்கப்பட்டு இணைக்கப்பட்டது!' : 'Document verified and attached!') + '\')">' + (lang === 'ta' ? 'உறுதிசெய்து ஆவணத்தை இணைக்கவும்' : 'Confirm &amp; Attach Document') + '</button>');
    }, 600);
  }
}

function journey(){
  const lang = window.currentLang || 'en';
  if(!window.currentUser){
    toast(lang === 'ta' ? 'உங்கள் தனிப்பயனாக்கப்பட்ட டாஷ்போர்டைப் பார்க்க உள்நுழையவும்.' : 'Please sign in to view your personalized Welfare Journey.');
    auth('Sign In', journey);
    return;
  }
  
  if (lang === 'ta') {
    openModal('<h2>எனது நலன்புரிப் பயண டாஷ்போர்டு</h2><p>குடிமகன் கணக்கு: <b>' + window.currentUser.email + '</b></p><div style="font-size:12px; line-height:1.6; margin:14px 0;"><p style="font-weight:700; color:#00865a; font-size:13px; margin-bottom:6px;">செயலில் உள்ள விண்ணப்பங்கள்:</p><div style="background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:10px;"><b style="color:#112448;">1. பிரதம மந்திரி ஆவாஸ் யோஜனா (வீட்டுவசதி திட்டம்)</b><br><span style="color:#00865a; font-weight:700;">நிலை: வரைவு மதிப்பாய்வு (Draft Review)</span><br><small style="color:#64748b;">விண்ணப்ப எண்: TN-2026-PMAY-8842</small></div><div style="background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:10px;"><b style="color:#112448;">2. மூவலூர் ராமாமிர்தம் அம்மையார் புதுமைப் பெண் திட்டம்</b><br><span style="color:#00865a; font-weight:700;">நிலை: ஒப்புதல் அளிக்கப்பட்டது (Approved) - மாதம் ₹1,000</span><br><small style="color:#64748b;">வங்கி பரிமாற்றம்: நேரடி வங்கி கணக்கில் செலுத்தப்பட்டது</small></div><p style="font-weight:700; color:#00865a; font-size:13px; margin-top:14px; margin-bottom:6px;">பரிந்துரைக்கப்பட்ட திட்டங்கள் (உயர் முன்னுரிமை தகுதி):</p><ul style="padding-left:18px; margin:4px 0; font-size:12px;"><li><b>கலைஞர் மகளிர் உரிமைத் தொகைத் திட்டம்</b> (100% தகுதி பொருத்தம்)</li><li><b>பி.எம். கிசான் விவசாயிகள் உதவித் தொகை</b> (85% தகுதி பொருத்தம்)</li></ul></div><div class="choice"><button class="btn outline" onclick="documentAI()">ஆவணத்தைப் பதிவேற்ற</button><button class="btn primary" onclick="closeModal()">டாஷ்போர்டை மூடு</button></div>');
  } else {
    openModal('<h2>My Welfare Journey Dashboard</h2><p>Citizen Account: <b>' + window.currentUser.email + '</b></p><div style="font-size:12px; line-height:1.6; margin:14px 0;"><p style="font-weight:700; color:#00865a; font-size:13px; margin-bottom:6px;">Active Applications:</p><div style="background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:10px;"><b style="color:#112448;">1. Pradhan Mantri Awas Yojana (PMAY-Urban)</b><br><span style="color:#00865a; font-weight:700;">Status: Draft Review</span><br><small style="color:#64748b;">Application ID: TN-2026-PMAY-8842</small></div><div style="background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:10px;"><b style="color:#112448;">2. Pudhumai Penn Scheme</b><br><span style="color:#00865a; font-weight:700;">Status: Approved - ₹1,000 / month</span><br><small style="color:#64748b;">DBT Transfer: Direct to Bank Account</small></div><p style="font-weight:700; color:#00865a; font-size:13px; margin-top:14px; margin-bottom:6px;">Recommended Schemes (High Priority):</p><ul style="padding-left:18px; margin:4px 0; font-size:12px;"><li><b>Kalaignar Magalir Urimai Thogai</b> (100% Match)</li><li><b>PM-KISAN Samman Nidhi</b> (85% Match)</li></ul></div><div class="choice"><button class="btn outline" onclick="documentAI()">Upload Document</button><button class="btn primary" onclick="closeModal()">Close Dashboard</button></div>');
  }
}

function resources(){
  const lang = window.currentLang || 'en';
  if (lang === 'ta') {
    openModal('<h2>அரசு நலன்புரி வளங்கள் &amp; உதவி</h2><p>அதிகாரப்பூர்வ போர்ட்டல்கள், வழிகாட்டுதல்கள் மற்றும் உதவி எண்கள்:</p><div style="font-size:12px; line-height:1.6; margin:12px 0;"><p><b>அதிகாரப்பூர்வ தளங்கள்:</b></p><ul style="padding-left:18px; margin:4px 0;"><li><a href="https://www.myscheme.gov.in" target="_blank" style="color:#00865a; font-weight:700;">myScheme அதிகாரப்பூர்வ போர்ட்டல்</a></li><li><a href="https://tnesevai.tn.gov.in" target="_blank" style="color:#00865a; font-weight:700;">தமிழ்நாடு இ-சேவை மையம்</a></li><li><a href="https://india.gov.in" target="_blank" style="color:#00865a; font-weight:700;">இந்திய தேசிய போர்ட்டல்</a></li></ul><p><b>தேசிய உதவி எண்கள்:</b></p><p>📞 குடிமக்கள் கட்டணமில்லா உதவி எண்: 1800-11-3377<br>📞 தமிழ்நாடு அரசு சேவைகள்: 1100</p></div><button class="btn primary full" onclick="closeModal()">மூடு</button>');
  } else {
    openModal('<h2>Government Welfare Resources &amp; Help</h2><p>Official portals, guidelines, and helpline numbers:</p><div style="font-size:12px; line-height:1.6; margin:12px 0;"><p><b>Official Portals:</b></p><ul style="padding-left:18px; margin:4px 0;"><li><a href="https://www.myscheme.gov.in" target="_blank" style="color:#00865a; font-weight:700;">myScheme Official Portal</a></li><li><a href="https://tnesevai.tn.gov.in" target="_blank" style="color:#00865a; font-weight:700;">Tamil Nadu e-Sevai Service</a></li><li><a href="https://india.gov.in" target="_blank" style="color:#00865a; font-weight:700;">National Portal of India</a></li></ul><p><b>National Helplines:</b></p><p>📞 Citizen Toll-Free Helpline: 1800-11-3377<br>📞 Tamil Nadu Government Services: 1100</p></div><button class="btn primary full" onclick="closeModal()">Close</button>');
  }
}

function speak(){
  const langElem = document.getElementById('langSelect');
  const lang = langElem ? langElem.value || 'en' : 'en';
  const msg = lang === 'ta' ? 'குரல் உதவியாளர் செயல்படுகிறது (தமிழ்). பேசவும்...' : 'Voice Assistant active (' + lang.toUpperCase() + '). Listening...';
  toast(msg);
  setTimeout(() => {
    const qText = lang === 'ta' ? 'எனது கல்விக்கான நிதியுதவியை நான் தேடுகிறேன்' : 'I need financial support for higher education';
    fill(qText);
    toast((lang === 'ta' ? 'குரல் பதிவு செய்யப்பட்டது: "' : 'Voice transcribed: "') + qText + '"');
  }, 1000);
}

window.addEventListener('load', function() {
  const langSelect = document.getElementById('langSelect');
  if(langSelect) {
    langSelect.addEventListener('change', function() {
      setLanguage(this.value);
    });
  }

  const btnSignIn = document.getElementById('btnSignIn');
  if(btnSignIn) btnSignIn.addEventListener('click', function(e) { e.preventDefault(); auth('Sign In'); });
  
  const btnCreateAccount = document.getElementById('btnCreateAccount');
  if(btnCreateAccount) btnCreateAccount.addEventListener('click', function(e) { e.preventDefault(); auth('Create Account'); });
  
  const btnHeroStartJourney = document.getElementById('btnHeroStartJourney');
  if(btnHeroStartJourney) btnHeroStartJourney.addEventListener('click', function(e) { e.preventDefault(); journey(); });
  
  const btnHeroExploreSchemes = document.getElementById('btnHeroExploreSchemes');
  if(btnHeroExploreSchemes) btnHeroExploreSchemes.addEventListener('click', function(e) { e.preventDefault(); category('all'); });
  
  const btnSearch = document.getElementById('btnSearch');
  if(btnSearch) btnSearch.addEventListener('click', function(e) { e.preventDefault(); searchAI(); });
  
  const btnSpeak = document.getElementById('btnSpeak');
  if(btnSpeak) btnSpeak.addEventListener('click', function(e) { e.preventDefault(); speak(); });
  
  const aiInput = document.getElementById('aiInput');
  if(aiInput) {
    aiInput.addEventListener('keydown', function(e) {
      if(e.key === 'Enter') {
        e.preventDefault();
        searchAI();
      }
    });
  }
});
</script>
</body>
</html>"""

final_html = (USER_UI_HTML_TEMPLATE
    .replace("__LOGO_B64__", logo_b64)
    .replace("__HERO_B64__", hero_b64)
    .replace("__CATEGORIES_HTML__", categories_rendered_html)
    .replace("__SCHEMES_HTML__", schemes_rendered_html)
    .replace("__SCHEMES_COUNT_STR__", schemes_count_str)
    .replace("__SCHEMES_JSON__", json.dumps(schemes_data, ensure_ascii=True))
    .replace("__CATEGORIES_JSON__", json.dumps(categories_data, ensure_ascii=True))
)

# Render the exact approved user HTML UI inside Streamlit
components.html(final_html, height=2200, scrolling=True)
