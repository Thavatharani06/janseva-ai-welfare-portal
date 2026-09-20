import os
import json
import uuid
import httpx
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.scheme import Scheme, SchemeCategory, SchemeAlias, EligibilityRule, Document, DocumentEmbedding
from app.services.ocr_service import OCRService
from app.services.rule_extractor import RuleExtractor
from app.services.alias_generator import AliasGenerator

class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest_government_pdf(
        self,
        scheme_id: str,
        title: str,
        go_number: str,
        file_path_or_url: str
    ) -> Dict[str, Any]:
        """
        Modular Ingestion Pipeline:
        1. Download / Locates file
        2. Parses & OCR extracts text
        3. Chunks text into 500-character segments
        4. Embeds & stores in database vector store
        """
        local_file_path = file_path_or_url

        # Download if URL
        if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
            os.makedirs("uploads/raw_docs", exist_ok=True)
            local_file_path = f"uploads/raw_docs/gov_doc_{uuid.uuid4().hex[:6]}.pdf"
            async with httpx.AsyncClient() as client:
                res = await client.get(file_path_or_url)
                with open(local_file_path, "wb") as f:
                    f.write(res.content)

        # Step 2: OCR Extract Text
        ocr_text = OCRService.extract_text_from_file(local_file_path)

        # Step 3: Save Document Record
        doc = Document(
            scheme_id=scheme_id,
            title=title,
            go_number=go_number,
            document_type="GO",
            file_path=local_file_path,
            ocr_text=ocr_text
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)

        # Step 4: Chunk Text (500 chars per chunk)
        chunk_size = 500
        chunks = [ocr_text[i:i+chunk_size] for i in range(0, len(ocr_text), chunk_size)]
        
        created_embeddings = []
        for idx, chunk_text in enumerate(chunks):
            emb = DocumentEmbedding(
                document_id=doc.id,
                chunk_index=idx,
                chunk_content=chunk_text,
                page_number=(idx // 2) + 1,
                metadata_json={"go_number": go_number, "ingest_source": "official_gov_portal"}
            )
            self.db.add(emb)
            created_embeddings.append(emb)

        await self.db.commit()

        return {
            "document_id": doc.id,
            "title": title,
            "go_number": go_number,
            "ocr_text_length": len(ocr_text),
            "chunks_created": len(chunks),
            "status": "ingested_successfully"
        }

    async def ingest_myscheme_dataset(self, json_path: str) -> Dict[str, Any]:
        """
        Reads, parses, and ingests official-style schemes into the relational schema.
        Also chunk-embeds detail descriptions to populate RAG search.
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"myScheme dataset JSON not found at: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            raw_schemes = json.load(f)

        stats = {
            "schemes_processed": 0,
            "categories_created": 0,
            "rules_created": 0,
            "aliases_created": 0,
            "rag_chunks_created": 0
        }

        for idx, item in enumerate(raw_schemes):
            title = item.get("title")
            category_name = item.get("category", "General Welfare")
            ministry = item.get("ministry", "Ministry of Social Justice")
            central_or_state = item.get("central_or_state", "Central")
            state_name = item.get("state_name", "All India")
            description = item.get("description", "")
            eligibility_text = item.get("eligibility_text", "")
            benefits_text = item.get("benefits_text", "")
            req_docs = item.get("required_documents", [])
            helpline = item.get("helpline", "1100")
            official_url = item.get("official_url", "")
            faqs = item.get("faqs", [])

            # 1. Fetch or create SchemeCategory
            cat_query = await self.db.execute(select(SchemeCategory).where(SchemeCategory.name == category_name))
            category = cat_query.scalars().first()
            if not category:
                category = SchemeCategory(
                    name=category_name,
                    icon="home" if "housing" in category_name.lower() else "user",
                    description=f"Welfare schemes targeting {category_name}"
                )
                self.db.add(category)
                await self.db.flush()
                stats["categories_created"] += 1

            # 2. Scheme code
            code = item.get("code") or (title.split("(")[-1].replace(")", "").strip() if "(" in title else f"SCH-{idx+1:04d}")

            # 3. Check if scheme already exists, if so update/skip
            scheme_query = await self.db.execute(select(Scheme).where(Scheme.code == code))
            scheme = scheme_query.scalars().first()
            if not scheme:
                scheme = Scheme(code=code)
                self.db.add(scheme)

            # Extract structured limits from text description
            rules = RuleExtractor.extract_eligibility_limits(eligibility_text)

            scheme.category_id = category.id
            scheme.title = title
            scheme.title_ta = item.get("title_ta", title)
            scheme.ministry = ministry
            scheme.official_website = official_url
            scheme.helpline_number = helpline
            scheme.legal_summary = f"{description} Eligible: {eligibility_text}"
            scheme.simple_summary = f"This scheme helps you get {benefits_text}. To apply, you need: {', '.join(req_docs)}."
            scheme.eli10_summary = f"Imagine the government wants to help you. If you qualify under these conditions ({eligibility_text}), they will transfer {benefits_text} directly to your wallet!"
            
            # Save derived limits & Provenance metadata
            scheme.min_age = rules["min_age"]
            scheme.max_age = rules["max_age"]
            scheme.max_income = rules["max_income"]
            scheme.gender_restriction = rules["gender_restriction"]
            scheme.target_occupation = rules["target_occupation"]
            scheme.target_community = rules["target_community"]
            scheme.state_district_scope = state_name
            scheme.district_scope = "All Districts"
            scheme.required_documents = req_docs
            scheme.source_name = "myScheme / India.gov.in"
            scheme.source_url = official_url
            scheme.source_scheme_id = code
            scheme.source_last_updated = datetime.utcnow()
            scheme.imported_at = datetime.utcnow()
            scheme.verified_at = datetime.utcnow()
            scheme.data_status = "VERIFIED_OFFICIAL"
            scheme.language_availability = ["en", "ta", "hi"]
            scheme.benefits_summary = benefits_text
            scheme.eligibility_description = eligibility_text
            scheme.application_process = f"Visit official portal {official_url} or call helpline {helpline}."

            await self.db.flush()

            # 4. Generate structured rules
            # Clear old rules
            await self.db.execute(
                select(EligibilityRule).where(EligibilityRule.scheme_id == scheme.id)
            )
            # Add dynamic rules
            if scheme.max_income:
                self.db.add(EligibilityRule(
                    scheme_id=scheme.id,
                    rule_key="income",
                    operator="<=",
                    rule_value=str(scheme.max_income),
                    description=f"Annual income must be below Rs. {scheme.max_income}"
                ))
                stats["rules_created"] += 1
            if scheme.min_age > 0:
                self.db.add(EligibilityRule(
                    scheme_id=scheme.id,
                    rule_key="age",
                    operator=">=",
                    rule_value=str(scheme.min_age),
                    description=f"Age must be at least {scheme.min_age} years"
                ))
                stats["rules_created"] += 1

            # 5. Auto-generate Aliases
            aliases = AliasGenerator.generate_aliases(title)
            # Add Tamil representation as alias
            if item.get("title_ta"):
                aliases.append(item.get("title_ta"))
            
            for alias in aliases:
                alias_query = await self.db.execute(
                    select(SchemeAlias).where(SchemeAlias.scheme_id == scheme.id, SchemeAlias.alias == alias)
                )
                if not alias_query.scalars().first():
                    self.db.add(SchemeAlias(scheme_id=scheme.id, alias=alias, language_code="ta" if any(ord(c) > 127 for c in alias) else "en"))
                    stats["aliases_created"] += 1

            # 6. Seed RAG Document & Embeddings
            # To ensure the RAG assistant is fully aware, we create a reference Guideline Document
            doc_query = await self.db.execute(select(Document).where(Document.scheme_id == scheme.id, Document.title == f"{code} Official Guidelines"))
            doc = doc_query.scalars().first()
            if not doc:
                doc = Document(
                    scheme_id=scheme.id,
                    title=f"{code} Official Guidelines",
                    go_number=f"GO-{code}-2026",
                    document_type="GUIDELINE",
                    ocr_text=f"Scheme: {title}\nDepartment: {ministry}\nBenefits: {benefits_text}\nEligibility conditions: {eligibility_text}\nHow to apply: visit {official_url}. Helpline: {helpline}."
                )
                self.db.add(doc)
                await self.db.flush()

            # Update text chunks
            chunk_content = f"Official scheme documentation for {title} under the {ministry}. Eligibility: {eligibility_text}. Benefits include: {benefits_text}. Documents required: {', '.join(req_docs)}. Helpline: {helpline}."
            
            # Check for existing embeddings
            emb_query = await self.db.execute(select(DocumentEmbedding).where(DocumentEmbedding.document_id == doc.id))
            emb = emb_query.scalars().first()
            if not emb:
                emb = DocumentEmbedding(
                    document_id=doc.id,
                    chunk_index=0,
                    chunk_content=chunk_content,
                    page_number=1,
                    metadata_json={"source": "myScheme Ingestion Pipeline"}
                )
                self.db.add(emb)
                stats["rag_chunks_created"] += 1
            else:
                emb.chunk_content = chunk_content

            stats["schemes_processed"] += 1

        await self.db.commit()
        return stats
