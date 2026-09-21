import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from app.core.database import AsyncSessionLocal
from app.repositories.scheme_repository import SchemeRepository
from app.services.speech_service import SpeechService

async def run_suite():
    async with AsyncSessionLocal() as db:
        repo = SchemeRepository(db)
        speech_service = SpeechService(db)
        
        print("==========================================================================")
        print("JANSEVA AI — COMPLETE VOICE & SEARCH FUNCTIONALITY VERIFICATION SUITE")
        print("==========================================================================")
        
        # 1. English Education Search
        res_en_edu = await repo.get_all(search="I need an education scheme")
        print(f"\n1. English Voice/Text Search ('I need an education scheme'): {len(res_en_edu)} schemes")
        assert len(res_en_edu) > 0 and len(res_en_edu) < 71 and any("Education" in (s.category_name or "") or "Scholarship" in s.title for s in res_en_edu)
        for s in res_en_edu[:3]:
            print(f"   - [{s.code}] {s.title} ({s.category_name})")

        # 2. Hindi Education Search
        res_hi_edu = await repo.get_all(search="मुझे शिक्षा के लिए सरकारी योजना चाहिए")
        print(f"\n2. Hindi Voice/Text Search: {len(res_hi_edu)} schemes")
        assert len(res_hi_edu) > 0 and any("Education" in (s.category_name or "") or "Scholarship" in s.title for s in res_hi_edu)
        for s in res_hi_edu[:3]:
            print(f"   - [{s.code}] {s.title} ({s.category_name})")

        # 3. Tamil Education Search & Voice Guidance
        res_ta_edu = await repo.get_all(search="எனக்கு கல்விக்கான அரசு திட்டம் வேண்டும்")
        v_ta = await speech_service.process_voice_input("test_user", raw_transcript="எனக்கு கல்விக்கான அரசு திட்டம் வேண்டும்", language="ta")
        print(f"\n3. Tamil Voice Search: {len(res_ta_edu)} schemes")
        speech_safe = v_ta['assistant_speech'].encode('ascii', errors='replace').decode('ascii')
        print(f"   Assistant Tamil Speech: {speech_safe}")
        assert len(res_ta_edu) > 0 and v_ta['assistant_speech'] is not None

        # 4. English Housing Search
        res_en_house = await repo.get_all(search="I need housing support")
        print(f"\n4. English Housing Search ('I need housing support'): {len(res_en_house)} schemes")
        assert len(res_en_house) > 0 and any("Housing" in (s.category_name or "") or "Awas" in s.title or "Green House" in s.title for s in res_en_house)
        for s in res_en_house[:3]:
            print(f"   - [{s.code}] {s.title} ({s.category_name})")

        # 5. Tamil Housing Search
        res_ta_house = await repo.get_all(search="எனக்கு வீடு கட்ட உதவி வேண்டும்")
        print(f"\n5. Tamil Housing Search: {len(res_ta_house)} schemes")
        assert len(res_ta_house) > 0 and any("Housing" in (s.category_name or "") or "Awas" in s.title or "Green House" in s.title for s in res_ta_house)
        for s in res_ta_house[:3]:
            print(f"   - [{s.code}] {s.title} ({s.category_name})")

        # 6. Hindi Housing Search
        res_hi_house = await repo.get_all(search="मुझे घर बनाने के लिए सहायता चाहिए")
        print(f"\n6. Hindi Housing Search: {len(res_hi_house)} schemes")
        assert len(res_hi_house) > 0 and any("Housing" in (s.category_name or "") or "Awas" in s.title or "Green House" in s.title for s in res_hi_house)
        for s in res_hi_house[:3]:
            print(f"   - [{s.code}] {s.title} ({s.category_name})")

        # 7. Structured Filters + State Combination
        res_tn_housing = await repo.get_all(state="Tamil Nadu", category_id="Housing & Urban Development")
        print(f"\n7. Structured Filter (Tamil Nadu + Housing & Urban Development): {len(res_tn_housing)} schemes")
        assert len(res_tn_housing) == 3
        for s in res_tn_housing:
            print(f"   - [{s.code}] {s.title} (Scope: {s.state_district_scope})")

        # 8. Reset Filters Case
        res_reset = await repo.get_all()
        print(f"\n8. Reset Filters (All Schemes): {len(res_reset)} schemes")
        assert len(res_reset) == 71

        # 9. No Matching Schemes Case
        res_none = await repo.get_all(search="xyzspacecraftconstruction123")
        print(f"\n9. Unmatched Query ('xyzspacecraftconstruction123'): {len(res_none)} schemes")
        assert len(res_none) == 0

        print("\n==========================================================================")
        print("ALL 9 VERIFICATION TEST CASES PASSED SUCCESSFULLY (100% GREEN)")
        print("==========================================================================")

if __name__ == "__main__":
    asyncio.run(run_suite())
