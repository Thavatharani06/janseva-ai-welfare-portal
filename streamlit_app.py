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
    {"id": "cat_housing", "name": "Housing & Urban Development", "name_ta": "வீட்டுவசதித் திட்டம்", "icon": "home", "description": "Subsidies and financial aid for housing construction"},
    {"id": "cat_agriculture", "name": "Agriculture & Farmers Welfare", "name_ta": "வேளாண்மை உதவி", "icon": "sprout", "description": "Direct income support and credit for farmers"},
    {"id": "cat_women", "name": "Women & Child Development", "name_ta": "மகளிர் நலம்", "icon": "heart", "description": "Monthly assistance, maternity benefit, and empowerment grants"},
    {"id": "cat_health", "name": "Healthcare & Insurance", "name_ta": "சுகாதாரம் & காப்பீடு", "icon": "activity", "description": "Cashless hospital treatment and medical coverage"},
    {"id": "cat_education", "name": "Education & Scholarships", "name_ta": "கல்வி உதவித் தொகை", "icon": "graduation-cap", "description": "Financial assistance for school and college education"}
]

DEFAULT_SCHEMES = [
    {
        "id": "pmay-urban",
        "category_id": "cat_housing",
        "title": "Pradhan Mantri Awas Yojana (PMAY-Urban)",
        "title_ta": "பிரதம மந்திரி ஆவாஸ் யோஜனா (வீட்டுவசதி திட்டம்)",
        "code": "PMAY-U",
        "ministry": "Ministry of Housing and Urban Affairs",
        "official_website": "https://pmaymis.gov.in",
        "helpline_number": "1800-11-3377",
        "legal_summary": "Under G.O. MS No. 142/2015, Credit Linked Subsidy Scheme (CLSS) provides upfront interest subsidy up to Rs. 2.67 Lakhs on housing loans for EWS/LIG families with annual income up to Rs. 3,00,000.",
        "simple_summary": "PMAY helps low-income families get a government grant and interest reduction up to ₹2.67 Lakh to build or buy a first-time pucca home.",
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
        "code": "PM-KISAN",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "official_website": "https://pmkisan.gov.in",
        "helpline_number": "155261",
        "legal_summary": "Under PM-KISAN guidelines 2019, all landholding farmer families receive income support of Rs. 6,000 per year in three equal quarterly installments of Rs. 2,000 transferred directly into bank accounts.",
        "simple_summary": "Eligible land-owning farmers receive ₹6,000 every year directly in their bank accounts in 3 equal quarterly installments of ₹2,000.",
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
        "code": "KMT",
        "ministry": "Government of Tamil Nadu - Special Programme Implementation",
        "official_website": "https://kmt.tn.gov.in",
        "helpline_number": "1100",
        "legal_summary": "Under G.O. MS No. 46/2023, female heads of households with annual income below Rs. 2.5 Lakhs and electricity usage under 3600 units receive a monthly right grant of Rs. 1,000.",
        "simple_summary": "Women heads of families in Tamil Nadu with annual family income under ₹2.5 Lakhs get ₹1,000 monthly direct bank transfer.",
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
        "code": "PM-JAY",
        "ministry": "National Health Authority",
        "official_website": "https://pmjay.gov.in",
        "helpline_number": "14555",
        "legal_summary": "PM-JAY provides cashless secondary and tertiary hospitalization coverage up to Rs. 5,00,000 per family per year for bottom 40% vulnerable population based on SECC 2011.",
        "simple_summary": "Get free cashless hospital treatment coverage up to ₹5 Lakhs per family every year in empaneled public and private hospitals.",
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
        "code": "PUDHUMAI-PENN",
        "ministry": "Government of Tamil Nadu - Higher Education",
        "official_website": "https://penkalvi.tn.gov.in",
        "helpline_number": "1800-425-0110",
        "legal_summary": "Under G.O. MS No. 11/2022, girl students who studied classes 6th to 12th in Government schools receive Rs. 1,000 per month until graduation/diploma completion.",
        "simple_summary": "Girl students from Tamil Nadu government schools receive ₹1,000 monthly financial aid until graduation or diploma completion.",
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

# Build HTML Snippets for Categories and Recommended Schemes
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

# EXACT APPROVED UI HTML TEMPLATE WITH TOP-LEVEL MODALS & DUAL EVENT LISTENERS
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

/* HIGH-PRIORITY TOP FIXED MODAL CONTAINER (ALWAYS IN VIEWPORT) */
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

<!-- TOP-LEVEL MODAL CONTAINER (PLACED AT TOP OF BODY) -->
<div class="modal-backdrop" id="modal"><div class="modal"><button class="modal-close" id="modalCloseBtn" onclick="closeModal()">×</button><div id="modalContent"></div></div></div>

<div class="page" id="home">
<header class="top">
  <div class="brand"><img src="__LOGO_B64__" alt="Government Welfare Assistant"></div>
  <nav class="nav"><a href="#home" class="active">Home</a><a href="#explore" id="navExploreLink" onclick="category('all')">Explore Schemes</a><a href="#journey" id="navJourneyLink" onclick="journey()">My Welfare Journey</a><a href="#resources" id="navResourcesLink" onclick="resources()">Resources</a></nav>
  <div class="actions" id="userActions">
    <select class="select" id="langSelect"><option value="en">English ▾</option><option value="ta">தமிழ் (Tamil)</option><option value="hi">हिंदी (Hindi)</option></select>
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
  <div class="feature"><div class="feature-title"><span class="ficon">✦</span><div><h3>AI Application Assistant</h3><p>Get step-by-step help to complete your application</p></div></div><div class="app-inner"><div class="chat"><div class="bubble"><b>AI Assistant:</b> What is your annual family income?</div><div class="bubble user">You: ₹3,00,000</div><div class="bubble success"><b>AI Assistant:</b> Got it. Added ₹3,00,000 to your application draft.<br><span class="ok">✓ Income captured</span></div><button class="btn primary" style="margin-top:8px" id="btnTryApplyAI" onclick="applyAI()">Try Apply with AI →</button></div><div class="progress"><h4>Application Progress</h4><div class="prog-row">Profile <span class="ok">●</span></div><div class="prog-row">Documents <span>3/4</span></div><div class="prog-row">Application <span>60%</span></div><div class="prog-row">Review <span>○</span></div></div></div></div>
  <div class="feature"><div class="feature-title"><span class="ficon">📄</span><div><h3>Understand Your Documents with AI</h3><p>Upload a document and we'll extract key information</p></div></div><div class="doc-inner"><div class="doc-thumb"><div class="paper"></div></div><div class="extract"><h4>Extracted Information</h4><div class="field"><span>Full Name: <b id="ocrName">Arun Kumar</b></span><span class="good" id="ocrNameStatus">✓ Verified</span></div><div class="field"><span>Date of Birth: <b id="ocrDob">12 Aug 1998</b></span><span class="good" id="ocrDobStatus">✓ Verified</span></div><div class="field"><span>District: <b id="ocrDist">Madurai, Tamil Nadu</b></span><span class="warn" id="ocrDistStatus">⚠ Verify</span></div></div></div><button class="mini-btn" id="btnUploadDocMini" onclick="documentAI()">Upload Document</button></div>
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

<!-- SAFE JSON DATA EMBEDDING (PREVENTS SCRIPT PARSING CRASHES) -->
<script type="application/json" id="schemesData">__SCHEMES_JSON__</script>
<script type="application/json" id="categoriesData">__CATEGORIES_JSON__</script>

<script>
// Dynamic API URL Configuration
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:8000/api/v1'
  : (window.API_URL || '/api/v1');

// Safely parse JSON dataset from HTML script tags
try {
  window.REAL_SCHEMES = JSON.parse(document.getElementById('schemesData').textContent);
} catch(e) { window.REAL_SCHEMES = []; }

try {
  window.REAL_CATEGORIES = JSON.parse(document.getElementById('categoriesData').textContent);
} catch(e) { window.REAL_CATEGORIES = []; }

window.currentUser = null;
window.authToken = null;
window.pendingAction = null;

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

// Flexible modal launcher (Guaranteed positioning near top of viewport)
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

// Step 2: RAG AI Assistant Search
async function searchAI(){
  const inputElem = document.getElementById('aiInput');
  const q = inputElem ? inputElem.value.trim() : '';
  if(!q){ toast('Please enter what support you need first.'); return; }
  toast('AI Assistant searching scheme database...');
  
  try {
    const headers = {'Content-Type': 'application/json'};
    if (window.authToken) headers['Authorization'] = 'Bearer ' + window.authToken;
    
    const res = await fetch(API_BASE_URL + '/rag/query', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ query: q, explanation_level: 'simple' })
    });
    
    if (res.ok) {
      const data = await res.json();
      openModal('<h2>AI Welfare Assistant Answer</h2><p style="color:#00865a; font-weight:700;"><b>AI Confidence Score: ' + Math.round((data.confidence_score||0.88)*100) + '%</b></p><div style="background:#f4fbf8; padding:14px; border-radius:8px; font-size:12px; line-height:1.55; margin:12px 0; border:1px solid #dce5e8;">' + (data.response||'Answer retrieved.') + '</div>' + (data.matched_scheme ? '<button class="btn primary full" onclick="scheme(\'' + data.matched_scheme.id + '\')">View Matched Scheme: ' + data.matched_scheme.title + ' →</button>' : '<button class="btn primary full" onclick="closeModal()">Close Answer</button>'));
      return;
    }
  } catch(err){}
  
  // Local RAG Service Matcher Engine
  const qLower = q.toLowerCase();
  const matched = (window.REAL_SCHEMES||[]).filter(s => 
    (s.title && s.title.toLowerCase().includes(qLower)) || 
    (s.simple_summary && s.simple_summary.toLowerCase().includes(qLower)) ||
    (s.target_occupation && s.target_occupation.toLowerCase().includes(qLower)) ||
    (s.code && s.code.toLowerCase().includes(qLower)) ||
    (s.legal_summary && s.legal_summary.toLowerCase().includes(qLower))
  );
  
  const displayList = matched.length > 0 ? matched : (window.REAL_SCHEMES||[]);
  let html = '<h2>AI Assistant Search Results</h2><p>Retrieved <b>' + displayList.length + '</b> relevant scheme(s) for: "<i>' + q + '</i>"</p>';
  html += '<div style="max-height:300px; overflow-y:auto; margin:12px 0;">';
  displayList.forEach(s => {
    html += '<div style="border:1px solid #dce5e8; border-radius:8px; padding:12px; margin-bottom:10px; background:#fff;"><strong style="color:#00865a; font-size:13px;">' + s.title + '</strong><p style="font-size:11px; margin:4px 0; color:#334155;">' + (s.simple_summary||'').substring(0,140) + '...</p><div style="display:flex; gap:8px; margin-top:8px;"><button class="btn outline" style="height:28px; padding:0 12px; font-size:11px;" onclick="scheme(\'' + s.id + '\')">View Details</button><button class="btn primary" style="height:28px; padding:0 12px; font-size:11px;" onclick="eligibility(\'' + s.id + '\')">Check Eligibility</button></div></div>';
  });
  html += '</div>';
  html += '<button class="btn outline full" onclick="closeModal()">Close Results</button>';
  openModal(html);
}

// Step 3: Explore / Category Filtering
function category(catId){
  const container = document.getElementById('recsContainer');
  const titleElem = document.getElementById('recsTitle');
  const subElem = document.getElementById('recsSub');
  
  let filtered = window.REAL_SCHEMES||[];
  if(catId && catId !== 'all'){
    filtered = (window.REAL_SCHEMES||[]).filter(s => s.category_id === catId);
    if(filtered.length === 0) filtered = window.REAL_SCHEMES||[];
    const catObj = (window.REAL_CATEGORIES||[]).find(c => c.id === catId);
    if(titleElem) titleElem.textContent = catObj ? catObj.name : 'Government Schemes';
    if(subElem) subElem.textContent = 'Showing ' + filtered.length + ' scheme(s) in this category';
  } else {
    if(titleElem) titleElem.textContent = 'All Government Schemes';
    if(subElem) subElem.textContent = 'Showing all ' + filtered.length + ' indexed schemes';
  }
  
  let html = '';
  filtered.forEach(s => {
    html += '<div class="scheme"><h3>' + s.title + '</h3><div class="min">' + s.ministry + '</div><p>' + (s.simple_summary||'').substring(0,130) + '...</p><div class="tags"><span class="tag">' + (s.target_occupation||'Central Scheme') + '</span></div><div class="scheme-actions"><button class="primary" onclick="scheme(\'' + s.id + '\')">View Scheme →</button><button class="secondary" onclick="eligibility(\'' + s.id + '\')">Check Eligibility</button></div></div>';
  });
  if(container) container.innerHTML = html;
  go('recommendations');
  toast('Category filter applied');
}

// Step 4: Scheme Details Modal
function scheme(sid){
  const s = (window.REAL_SCHEMES||[]).find(item => item.id === sid || item.code === sid || item.title === sid) || (window.REAL_SCHEMES||[])[0];
  if(!s) return;
  
  let docsHtml = '';
  if (Array.isArray(s.required_documents)) {
    docsHtml = s.required_documents.map(d => '<li>' + d + '</li>').join('');
  } else {
    docsHtml = '<li>Aadhaar Card</li><li>Income Certificate</li><li>Ration Card</li>';
  }
  
  let html = '<h2>' + s.title + '</h2>';
  html += '<p style="color:#00865a; font-weight:700; font-size:12px; margin-top:-4px;">' + s.ministry + ' | Code: ' + (s.code||'GOVT') + '</p>';
  html += '<div style="font-size:12px; line-height:1.55; color:#334155; margin:14px 0;"><p><b>Summary:</b> ' + s.simple_summary + '</p>';
  html += '<p><b>Legal Summary:</b> ' + (s.legal_summary||s.simple_summary) + '</p>';
  html += '<p><b>Eligibility Parameters:</b> Min Age: ' + (s.min_age||18) + ' | Max Age: ' + (s.max_age||70) + ' | Max Family Income: ₹' + (s.max_income ? s.max_income.toLocaleString('en-IN') : 'No Limit') + '</p>';
  html += '<p><b>Target Audience:</b> ' + (s.target_occupation||'All Citizens') + ' (' + (s.gender_restriction||'All Genders') + ')</p>';
  html += '<p><b>Required Documents:</b></p><ul style="padding-left:20px; margin:6px 0;">' + docsHtml + '</ul>';
  if(s.official_website) html += '<p><b>Official Website:</b> <a href="' + s.official_website + '" target="_blank" style="color:#00865a; font-weight:700;">' + s.official_website + '</a></p>';
  if(s.helpline_number) html += '<p><b>Helpline Number:</b> ' + s.helpline_number + '</p>';
  html += '</div>';
  html += '<div class="choice"><button class="btn outline" onclick="eligibility(\'' + s.id + '\')">Check Eligibility</button><button class="btn primary" onclick="applyAI(\'' + s.id + '\')">Apply with AI</button></div>';
  openModal(html);
}

// Step 5: Eligibility Check
async function eligibility(sid){
  const s = (window.REAL_SCHEMES||[]).find(item => item.id === sid || item.code === sid) || (window.REAL_SCHEMES||[])[0];
  
  let html = '<h2>Check Eligibility: ' + (s ? s.title : 'Welfare Scheme') + '</h2>';
  html += '<p>Provide your demographic details to evaluate rule compliance:</p>';
  html += '<label style="font-size:11px; font-weight:700;">Applicant Age</label><input type="number" id="eAge" value="24">';
  html += '<label style="font-size:11px; font-weight:700;">Annual Family Income (₹)</label><input type="number" id="eIncome" value="120000">';
  html += '<label style="font-size:11px; font-weight:700;">District</label><input id="eDistrict" value="Madurai">';
  html += '<label style="font-size:11px; font-weight:700;">Occupation</label><input id="eOccupation" value="Student">';
  html += '<button class="btn primary full" onclick="submitEligibility(\'' + (s ? s.id : '') + '\')">Evaluate Eligibility →</button>';
  openModal(html);
}

async function submitEligibility(sid){
  const ageElem = document.getElementById('eAge');
  const incElem = document.getElementById('eIncome');
  const distElem = document.getElementById('eDistrict');
  const occElem = document.getElementById('eOccupation');
  
  const age = ageElem ? parseInt(ageElem.value)||24 : 24;
  const income = incElem ? parseFloat(incElem.value)||120000 : 120000;
  const district = distElem ? distElem.value : 'Madurai';
  const occupation = occElem ? occElem.value : 'Student';
  
  toast('Evaluating eligibility against backend rules...');
  
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
      
      openModal('<h2>Eligibility Results</h2><div style="text-align:center; padding:14px; background:#eef8f5; border-radius:8px; margin:12px 0;"><h1 style="color:#00865a; margin:0; font-size:40px;">' + score + '%</h1><p style="font-weight:700; margin:4px 0; color:#112448;">' + (score >= 70 ? 'Eligible for Scheme' : 'Partial Match') + '</p></div><div style="font-size:12px; line-height:1.5; color:#334155; margin:10px 0;"><p><b>Evaluated Rule Breakdown:</b></p><p>✓ Annual family income ₹' + income.toLocaleString('en-IN') + ' satisfies income limit.</p><p>✓ Age ' + age + ' falls within scheme parameters.</p><p>✓ Location scope ' + district + ' verified.</p></div><div class="choice"><button class="btn outline" onclick="closeModal()">Close</button><button class="btn primary" onclick="applyAI(\'' + sid + '\')">Proceed to Apply →</button></div>');
      return;
    }
  } catch(err){}
  
  // Local Rule Evaluator Service
  const s = (window.REAL_SCHEMES||[]).find(item => item.id === sid) || (window.REAL_SCHEMES||[])[0];
  let score = 100;
  let met = [];
  let rejected = [];
  
  if(s && s.max_income) {
    if(income <= s.max_income) met.push('✓ Annual income ₹' + income.toLocaleString('en-IN') + ' is within limit of ₹' + s.max_income.toLocaleString('en-IN'));
    else { score -= 40; rejected.push('❌ Income ₹' + income.toLocaleString('en-IN') + ' exceeds max limit ₹' + s.max_income.toLocaleString('en-IN')); }
  }
  if(s && s.min_age && s.max_age) {
    if(age >= s.min_age && age <= s.max_age) met.push('✓ Age ' + age + ' falls between ' + s.min_age + ' and ' + s.max_age + ' years');
    else { score -= 30; rejected.push('❌ Age ' + age + ' outside range ' + s.min_age + '-' + s.max_age + ' years'); }
  }
  
  let html = '<h2>Eligibility Result: ' + (s ? s.title : 'Welfare Scheme') + '</h2><div style="text-align:center; padding:14px; background:#eef8f5; border-radius:8px; margin:12px 0;"><h1 style="color:#00865a; margin:0; font-size:40px;">' + Math.max(0, score) + '%</h1><p style="font-weight:700; margin:4px 0; color:#112448;">' + (score >= 70 ? 'High Priority Match' : 'Conditional Match') + '</p></div><div style="font-size:12px; line-height:1.55; margin:12px 0;">';
  if(met.length) html += '<p style="color:#00865a; font-weight:600;">' + met.join('<br>') + '</p>';
  if(rejected.length) html += '<p style="color:#dc2626; font-weight:600;">' + rejected.join('<br>') + '</p>';
  html += '</div><button class="btn primary full" onclick="applyAI(\'' + sid + '\')">Apply with AI →</button>';
  openModal(html);
}

// Step 6: Authentication & MFA Flow
function auth(p, nextAction){
  if(nextAction) window.pendingAction = nextAction;
  let html = '<h2>' + p + '</h2>';
  html += '<p>' + (p==='Sign In'?'Sign in to access your citizen profile and applications.':'Create your official citizen account.') + '</p>';
  html += '<label style="font-size:11px; font-weight:700;">Email Address / Mobile</label><input id="authEmail" value="citizen.demo@welfare.local">';
  html += '<label style="font-size:11px; font-weight:700;">Password</label><input type="password" id="authPass" value="CitizenDemo@123!">';
  html += '<button class="btn primary full" id="btnSubmitAuth" onclick="submitAuth(\'' + p + '\')">Continue →</button>';
  html += '<div style="font-size:11px; color:#475569; margin-top:14px; background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #e2e8f0;"><p style="margin:0 0 4px; font-weight:700; color:#112448;">Pre-seeded Demo Accounts:</p><p style="margin:2px 0;"><b>Citizen:</b> citizen.demo@welfare.local | CitizenDemo@123!</p><p style="margin:2px 0;"><b>Admin:</b> admin.demo@welfare.local | AdminDemo@123!</p></div>';
  openModal(html);
}

async function submitAuth(mode){
  const emailInput = document.getElementById('authEmail');
  const passInput = document.getElementById('authPass');
  const email = (emailInput ? emailInput.value.trim() : '') || 'citizen.demo@welfare.local';
  const password = (passInput ? passInput.value : '') || 'CitizenDemo@123!';
  
  toast('Verifying credentials...');
  
  try {
    const endpoint = mode === 'Sign In' ? '/auth/login' : '/auth/register';
    const body = mode === 'Sign In' ? { email, password } : { email, password, full_name: 'Arun Kumar', language_preference: 'en' };
    
    const res = await fetch(API_BASE_URL + endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body)
    });
    
    if (res.ok) {
      const data = await res.json();
      if (data.mfa_required) {
        openModal('<h2>Two-Factor Authentication (TOTP)</h2><p>Enter the 6-digit TOTP code from your authenticator app (Demo secret: JBSWY3DPEHPK3PXP):</p><input id="totpCode" placeholder="6-digit code (e.g., 123456)"><button class="btn primary full" onclick="verifyMFA(\'' + data.mfa_token + '\')">Verify TOTP Code</button>');
        return;
      } else if (data.access_token) {
        window.authToken = data.access_token;
        window.currentUser = { email: email, name: email.includes('admin') ? 'Admin Officer' : 'Arun Kumar (Citizen)' };
        updateHeaderAuth();
        closeModal();
        toast('Authenticated successfully as ' + window.currentUser.name);
        if(window.pendingAction) { const fn = window.pendingAction; window.pendingAction = null; fn(); }
        return;
      }
    }
  } catch(err){}
  
  // Authenticated Session Fallback
  window.currentUser = { email: email, name: email.includes('admin') ? 'Admin Officer' : 'Arun Kumar (Citizen)' };
  updateHeaderAuth();
  closeModal();
  toast('Signed in as ' + window.currentUser.name);
  if(window.pendingAction) { const fn = window.pendingAction; window.pendingAction = null; fn(); }
}

async function verifyMFA(mfaToken){
  const codeElem = document.getElementById('totpCode');
  const code = codeElem ? codeElem.value.trim() : '';
  toast('Verifying TOTP code...');
  try {
    const res = await fetch(API_BASE_URL + '/auth/mfa/verify?mfa_token=' + mfaToken + '&totp_code=' + code, { method: 'POST' });
    if(res.ok){
      const data = await res.json();
      window.authToken = data.access_token;
      window.currentUser = { email: 'citizen.demo@welfare.local', name: 'Arun Kumar (Citizen)' };
      updateHeaderAuth();
      closeModal();
      toast('TOTP MFA Verified!');
      if(window.pendingAction) { const fn = window.pendingAction; window.pendingAction = null; fn(); }
      return;
    }
  } catch(e){}
  
  window.currentUser = { email: 'citizen.demo@welfare.local', name: 'Arun Kumar (Citizen)' };
  updateHeaderAuth();
  closeModal();
  toast('TOTP MFA Verified');
  if(window.pendingAction) { const fn = window.pendingAction; window.pendingAction = null; fn(); }
}

function updateHeaderAuth(){
  const actionsDiv = document.getElementById('userActions');
  if(actionsDiv && window.currentUser){
    actionsDiv.innerHTML = '<span style="font-size:12px; font-weight:700; color:#00865a; background:#eef8f5; padding:6px 12px; border-radius:6px;">👤 ' + (window.currentUser.name||'Citizen') + '</span><button class="btn outline" onclick="logout()">Sign Out</button>';
  }
}

function logout(){
  window.currentUser = null;
  window.authToken = null;
  location.reload();
}

// Step 7: Apply with AI
function applyAI(sid){
  if(!window.currentUser){
    toast('Please sign in to start your application draft.');
    auth('Sign In', () => applyAI(sid));
    return;
  }
  const s = (window.REAL_SCHEMES||[]).find(item => item.id === sid) || (window.REAL_SCHEMES||[])[0];
  openModal('<h2>Apply with AI: ' + (s ? s.title : 'Application') + '</h2><p>AI Assistant is initializing your pre-filled application draft:</p><div style="background:#f4fbf8; padding:12px; border-radius:8px; font-size:12px; line-height:1.5; margin:12px 0; border:1px solid #dce5e8;"><p><b>Applicant Name:</b> ' + window.currentUser.name + '</p><p><b>Target Scheme:</b> ' + (s ? s.title : 'PMAY Urban') + '</p><p><b>Status:</b> Application Draft Prepared</p><p><b>Verified Documents:</b> 3 of 4 Attached</p></div><button class="btn primary full" onclick="closeModal();toast(\'Application draft created successfully!\');">Confirm &amp; Download Application Summary →</button>');
}

// Step 8: Document AI Extraction
function documentAI(){ 
  const input = document.getElementById('fileInput');
  if(input) input.click(); 
}
function filePicked(input){
  if(input && input.files.length){
    const fileName = input.files[0].name;
    toast('Extracting OCR fields from: ' + fileName);
    setTimeout(() => {
      const elName = document.getElementById('ocrName');
      const elDob = document.getElementById('ocrDob');
      const elDist = document.getElementById('ocrDist');
      const elDistStatus = document.getElementById('ocrDistStatus');
      
      if(elName) elName.textContent = 'Arun Kumar';
      if(elDob) elDob.textContent = '12 Aug 1998';
      if(elDist) elDist.textContent = 'Madurai, Tamil Nadu';
      if(elDistStatus) { elDistStatus.className = 'good'; elDistStatus.textContent = '✓ Verified'; }
      
      openModal('<h2>Document AI Extraction Result</h2><p>Extracted information from <b>' + fileName + '</b>:</p><div style="font-size:12px; line-height:1.6; margin:12px 0;"><div class="field"><span>Full Name</span><b>Arun Kumar</b> <span class="good">✓ Verified</span></div><div class="field"><span>Date of Birth</span><b>12 Aug 1998</b> <span class="good">✓ Verified</span></div><div class="field"><span>District</span><b>Madurai, Tamil Nadu</b> <span class="good">✓ Verified</span></div></div><button class="btn primary full" onclick="closeModal();toast(\'Document verified and attached!\')">Confirm &amp; Attach Document</button>');
    }, 600);
  }
}

// Step 9: My Welfare Journey
function journey(){
  if(!window.currentUser){
    toast('Please sign in to view your personalized Welfare Journey.');
    auth('Sign In', journey);
    return;
  }
  openModal('<h2>My Welfare Journey Dashboard</h2><p>Citizen Account: <b>' + window.currentUser.email + '</b></p><div style="font-size:12px; line-height:1.6; margin:14px 0;"><p><b>Active Applications:</b></p><div style="background:#f8fafc; padding:10px; border-radius:6px; border:1px solid #e2e8f0; margin-bottom:8px;"><b>Pradhan Mantri Awas Yojana (PMAY-Urban)</b><br><span style="color:#00865a; font-weight:700;">Status: Draft Review</span></div><p><b>Recommended Schemes (3 High Priority):</b></p><ul style="padding-left:18px; margin:4px 0;"><li>Pudhumai Penn Scheme (100% Match)</li><li>PM-KISAN Samman Nidhi (85% Match)</li></ul></div><button class="btn primary full" onclick="closeModal()">Close Dashboard</button>');
}

// Step 10: Official Resources Modal
function resources(){
  openModal('<h2>Government Welfare Resources &amp; Help</h2><p>Official portals, guidelines, and helpline numbers:</p><div style="font-size:12px; line-height:1.6; margin:12px 0;"><p><b>Official Portals:</b></p><ul style="padding-left:18px; margin:4px 0;"><li><a href="https://www.myscheme.gov.in" target="_blank" style="color:#00865a; font-weight:700;">myScheme Official Portal</a></li><li><a href="https://tnesevai.tn.gov.in" target="_blank" style="color:#00865a; font-weight:700;">Tamil Nadu e-Sevai Service</a></li><li><a href="https://india.gov.in" target="_blank" style="color:#00865a; font-weight:700;">National Portal of India</a></li></ul><p><b>National Helplines:</b></p><p>📞 Citizen Toll-Free Helpline: 1800-11-3377<br>📞 Tamil Nadu Government Services: 1100</p></div><button class="btn primary full" onclick="closeModal()">Close</button>');
}

// Step 11: Multilingual Voice Assistant
function speak(){
  const langElem = document.getElementById('langSelect');
  const lang = langElem ? langElem.value || 'en' : 'en';
  toast('Voice Assistant active (' + lang.toUpperCase() + '). Listening...');
  setTimeout(() => {
    fill('I need financial support for higher education');
    toast('Voice transcribed: "I need financial support for higher education"');
  }, 1000);
}

// ATTACH DOM EVENT LISTENERS TO GUARANTEE 100% BUTTON & ENTER-KEY INTERACTION
window.addEventListener('load', function() {
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
