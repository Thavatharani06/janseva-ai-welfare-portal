from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from app.models.scheme import SchemeCategory, Scheme, SchemeAlias, Document, DocumentEmbedding
from app.models.user import User
from app.core.security import hash_password, generate_recovery_codes

async def seed_initial_welfare_data(db: AsyncSession):
    """Seed core categories, schemes, aliases, and initial demo accounts."""
    
    # 1. Seed DEMO CITIZEN Account (Development/Demo)
    demo_citizen_res = await db.execute(select(User).where(User.email == "citizen.demo@welfare.local"))
    demo_citizen = demo_citizen_res.scalars().first()
    if not demo_citizen:
        demo_citizen = User(
            email="citizen.demo@welfare.local",
            hashed_password=hash_password("CitizenDemo@123!"),
            full_name="Arun Kumar (Demo Citizen)",
            role="citizen",
            language_preference="en",
            district="Madurai",
            age=24,
            gender="male",
            annual_income=120000.0,
            occupation="Student",
            community="OBC",
            mfa_secret="JBSWY3DPEHPK3PXP",
            is_mfa_enabled=True,
            mfa_recovery_codes=json.dumps(generate_recovery_codes(8)),
            is_onboarded=True
        )
        db.add(demo_citizen)
        await db.commit()

    # 2. Seed DEMO ADMIN Account (Development/Demo)
    demo_admin_res = await db.execute(select(User).where(User.email == "admin.demo@welfare.local"))
    demo_admin = demo_admin_res.scalars().first()
    if not demo_admin:
        demo_admin = User(
            email="admin.demo@welfare.local",
            hashed_password=hash_password("AdminDemo@123!"),
            full_name="Welfare Officer (Demo Admin)",
            role="admin",
            language_preference="en",
            district="Chennai",
            mfa_secret="JBSWY3DPEHPK3PXQ",
            is_mfa_enabled=True,
            mfa_recovery_codes=json.dumps(generate_recovery_codes(8)),
            is_onboarded=True
        )
        db.add(demo_admin)
        await db.commit()

    # 3. Ingest Authentic myScheme Dataset (200+ verified schemes)
    from app.services.ingestion_service import IngestionService
    import os

    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "myscheme_dataset", "schemes.json")
    if os.path.exists(json_path):
        ingestion_svc = IngestionService(db)
        await ingestion_svc.ingest_myscheme_dataset(json_path)

    # Check if categories exist
    cat_result = await db.execute(select(SchemeCategory))
    categories = cat_result.scalars().all()
    if categories:
        return  # Already seeded

    # Seed Categories
    cat_housing = SchemeCategory(name="Housing & Urban Development", name_ta="வீட்டுவசதித் திட்டம்", icon="home", description="Subsidies and financial aid for housing construction")
    cat_agriculture = SchemeCategory(name="Agriculture & Farmers Welfare", name_ta="வேளாண்மை உதவி", icon="sprout", description="Direct income support and credit for farmers")
    cat_women = SchemeCategory(name="Women & Child Development", name_ta="மகளிர் நலம்", icon="heart", description="Monthly assistance, maternity benefit, and empowerment grants")
    cat_health = SchemeCategory(name="Healthcare & Insurance", name_ta="சுகாதாரம் & காப்பீடு", icon="activity", description="Cashless hospital treatment and medical coverage")
    cat_education = SchemeCategory(name="Education & Scholarships", name_ta="கல்வி உதவித் தொகை", icon="graduation-cap", description="Financial assistance for school and college education")

    db.add_all([cat_housing, cat_agriculture, cat_women, cat_health, cat_education])
    await db.commit()

    # Seed Schemes with Aliases & Embeddings
    schemes_data = [
        {
            "category_id": cat_housing.id,
            "title": "Pradhan Mantri Awas Yojana (PMAY-Urban)",
            "title_ta": "பிரதம மந்திரி ஆவாஸ் யோஜனா (வீட்டுவசதி திட்டம்)",
            "code": "PMAY-U",
            "ministry": "Ministry of Housing and Urban Affairs",
            "official_website": "https://pmaymis.gov.in",
            "helpline_number": "1800-11-3377",
            "legal_summary": "Under G.O. MS No. 142/2015, Credit Linked Subsidy Scheme (CLSS) provides upfront interest subsidy up to Rs. 2.67 Lakhs on housing loans for EWS/LIG families with annual income up to Rs. 3,00,000.",
            "simple_summary": "PMAY helps low-income families get a government grant and interest reduction to build or buy a home.",
            "eli10_summary": "Imagine the government giving your family money to help build your dream house so everyone gets a safe room to sleep in!",
            "min_age": 18,
            "max_age": 70,
            "max_income": 300000.0,
            "gender_restriction": "All",
            "required_documents": ["Aadhaar Card", "Income Certificate", "Ration Card", "Bank Passbook", "Property Land Deed"],
            "aliases": [
                ("PMAY", "en"),
                ("Housing Scheme", "en"),
                ("House Subsidy", "en"),
                ("வீடு கட்ட உதவி", "ta"),
                ("வீட்டுவசதி திட்டம்", "ta"),
                ("Home Scheme", "en"),
                ("आवास योजना", "hi")
            ],
            "go_number": "G.O. MS No. 142/2015"
        },
        {
            "category_id": cat_agriculture.id,
            "title": "PM-KISAN Samman Nidhi Scheme",
            "title_ta": "பி.எம். கிசான் விவசாயிகள் உதவித் தொகை",
            "code": "PM-KISAN",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "official_website": "https://pmkisan.gov.in",
            "helpline_number": "155261",
            "legal_summary": "Under PM-KISAN guidelines 2019, all landholding farmer families receive income support of Rs. 6,000 per year in three equal quarterly installments of Rs. 2,000 transferred directly into bank accounts.",
            "simple_summary": "Eligible land-owning farmers receive Rs. 6,000 every year directly in their bank accounts in 3 installments.",
            "eli10_summary": "The government sends 2,000 rupees three times a year to farmers to buy seeds and fertilizer for crops!",
            "min_age": 18,
            "max_age": 100,
            "max_income": 500000.0,
            "gender_restriction": "All",
            "target_occupation": "Farmer",
            "required_documents": ["Aadhaar Card", "Land Patta Certificate", "Bank Account Passbook"],
            "aliases": [
                ("PM-KISAN", "en"),
                ("PM KISAN", "en"),
                ("Farmer Scheme", "en"),
                ("விவசாயி உதவித் தொகை", "ta"),
                ("6000 Rs Scheme", "en"),
                ("किसान सम्मान निधि", "hi")
            ],
            "go_number": "PM-KISAN Circular No. 1-1/2019"
        },
        {
            "category_id": cat_women.id,
            "title": "Kalaignar Magalir Urimai Thogai Scheme",
            "title_ta": "கலைஞர் மகளிர் உரிமைத் தொகைத் திட்டம்",
            "code": "KMT",
            "ministry": "Government of Tamil Nadu - Special Programme Implementation",
            "official_website": "https://kmt.tn.gov.in",
            "helpline_number": "1100",
            "legal_summary": "Under G.O. MS No. 46/2023, female heads of households with annual income below Rs. 2.5 Lakhs and electricity usage under 3600 units receive a monthly right grant of Rs. 1,000.",
            "simple_summary": "Women heads of families in Tamil Nadu with income under Rs. 2.5 Lakhs get Rs. 1,000 monthly bank transfer.",
            "eli10_summary": "Every month, moms get 1,000 rupees from the government to help run the house smoothly!",
            "min_age": 21,
            "max_age": 100,
            "max_income": 250000.0,
            "gender_restriction": "Female",
            "state_district_scope": "Tamil Nadu",
            "required_documents": ["Aadhaar Card", "Smart Ration Card", "Electricity Bill", "Bank Passbook"],
            "aliases": [
                ("KMT", "en"),
                ("Magalir Urimai", "en"),
                ("1000 Rs Scheme TN", "en"),
                ("மகளிர் உரிமைத் தொகை", "ta"),
                ("மகளிர் திட்டம்", "ta"),
                ("Women 1000 Grant", "en")
            ],
            "go_number": "TN G.O. MS No. 46/2023"
        },
        {
            "category_id": cat_health.id,
            "title": "Ayushman Bharat PM-JAY Health Insurance",
            "title_ta": "ஆயுஷ்மான் பாரத் மருத்துவக் காப்பீடு",
            "code": "PM-JAY",
            "ministry": "National Health Authority",
            "official_website": "https://pmjay.gov.in",
            "helpline_number": "14555",
            "legal_summary": "PM-JAY provides cashless secondary and tertiary hospitalization coverage up to Rs. 5,00,000 per family per year for bottom 40% vulnerable population based on SECC 2011.",
            "simple_summary": "Get free hospital treatment coverage up to Rs. 5 Lakhs per family every year in empaneled hospitals.",
            "eli10_summary": "If anyone in your family gets sick and needs hospital treatment, the health card pays up to 5 lakh rupees!",
            "min_age": 0,
            "max_age": 120,
            "max_income": 250000.0,
            "gender_restriction": "All",
            "required_documents": ["Aadhaar Card", "Ration Card"],
            "aliases": [
                ("Ayushman Bharat", "en"),
                ("PM-JAY", "en"),
                ("Health Card 5 Lakhs", "en"),
                ("ஆயுஷ்மான் பாரத்", "ta"),
                ("மருத்துவக் காப்பீடு", "ta")
            ],
            "go_number": "NHA Operational Guidelines 2018"
        },
        {
            "category_id": cat_education.id,
            "title": "Pudhumai Penn Scheme (Moovalur Ramamirtham Ammiyar)",
            "title_ta": "மூவலூர் ராமாமிர்தம் அம்மையார் புதுமைப் பெண் திட்டம்",
            "code": "PUDHUMAI-PENN",
            "ministry": "Government of Tamil Nadu - Higher Education",
            "official_website": "https://penkalvi.tn.gov.in",
            "helpline_number": "1800-425-0110",
            "legal_summary": "Under G.O. MS No. 11/2022, girl students who studied classes 6th to 12th in Government schools receive Rs. 1,000 per month until graduation/diploma completion.",
            "simple_summary": "Girl students from government schools get Rs. 1,000 monthly to pursue college or diploma education.",
            "eli10_summary": "Girls who finish government school get 1,000 rupees every month while studying in college!",
            "min_age": 17,
            "max_age": 25,
            "gender_restriction": "Female",
            "target_occupation": "Student",
            "state_district_scope": "Tamil Nadu",
            "required_documents": ["Aadhaar Card", "10th & 12th Marksheets", "6th-12th Govt School Bonafide", "Bank Passbook"],
            "aliases": [
                ("Pudhumai Penn", "en"),
                ("Moovalur Ramamirtham", "en"),
                ("Higher Education Girl Grant", "en"),
                ("புதுமைப் பெண் திட்டம்", "ta"),
                ("மாணவிகள் உதவித் தொகை", "ta")
            ],
            "go_number": "TN G.O. MS No. 11/2022"
        }
    ]

    for data in schemes_data:
        aliases_data = data.pop("aliases")
        go_num = data.pop("go_number")

        scheme = Scheme(**data)
        db.add(scheme)
        await db.commit()

        # Add aliases
        for alias_text, lang in aliases_data:
            db.add(SchemeAlias(scheme_id=scheme.id, alias=alias_text, language_code=lang))

        # Add Document & Embedding sample
        doc = Document(
            scheme_id=scheme.id,
            title=f"Official Gazette Notification - {scheme.title}",
            go_number=go_num,
            document_type="GO",
            ocr_text=f"{scheme.legal_summary} Eligibility details: Income ceiling Rs. {scheme.max_income}, age {scheme.min_age}-{scheme.max_age}."
        )
        db.add(doc)
        await db.commit()

        embed = DocumentEmbedding(
            document_id=doc.id,
            chunk_index=0,
            chunk_content=doc.ocr_text,
            page_number=1,
            metadata_json={"scheme_code": scheme.code, "go_number": go_num}
        )
        db.add(embed)

    await db.commit()
