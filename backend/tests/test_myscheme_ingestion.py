import os
import pytest
from app.services.rule_extractor import RuleExtractor
from app.services.alias_generator import AliasGenerator
from app.services.ingestion_service import IngestionService
from app.core.database import AsyncSessionLocal
from app.models.scheme import Scheme, SchemeCategory, SchemeAlias, EligibilityRule, DocumentEmbedding
from sqlalchemy.future import select

def test_rule_extractor():
    text = "Women above 21 years with annual family income below Rs. 2.5 Lakhs."
    rules = RuleExtractor.extract_eligibility_limits(text)
    
    assert rules["min_age"] == 21
    assert rules["max_income"] == 250000.0
    assert rules["gender_restriction"] == "Female"

    text2 = "Farmers aged between 18 and 60 years owning land up to 5 acres."
    rules2 = RuleExtractor.extract_eligibility_limits(text2)
    assert rules2["min_age"] == 18
    assert rules2["max_age"] == 60
    assert rules2["target_occupation"] == "Farmer"

def test_alias_generator():
    aliases = AliasGenerator.generate_aliases("Pradhan Mantri Awas Yojana - Urban (PMAY-U)")
    assert "PMAY" in aliases or "PMAY-U" in aliases or "Awas Yojana" in aliases
    assert len(aliases) > 0

@pytest.mark.asyncio
async def test_myscheme_ingestion_pipeline():
    async with AsyncSessionLocal() as session:
        service = IngestionService(session)
        dataset_path = "data/myscheme_dataset/schemes.json"
        
        # Verify JSON file exists
        assert os.path.exists(dataset_path)
        
        # Run Ingestion
        metrics = await service.ingest_myscheme_dataset(dataset_path)
        
        assert metrics["schemes_processed"] > 0
        assert metrics["aliases_created"] >= 0

        
        # Query DB to verify Scheme loaded with eligibility limits
        scheme_query = await session.execute(
            select(Scheme).where(Scheme.code == "PMAY-U")
        )
        pmay = scheme_query.scalars().first()
        assert pmay is not None
        assert pmay.min_age == 0
        assert pmay.max_income == 300000.0
        
        # Verify Tamil Alias Loaded
        alias_query = await session.execute(
            select(SchemeAlias).where(SchemeAlias.scheme_id == pmay.id)
        )
        aliases = alias_query.scalars().all()
        alias_texts = [a.alias for a in aliases]
        assert any("வீடு" in text or "Awas" in text or "PMAY" in text for text in alias_texts)
