import sys
import os
sys.path.insert(0, '.')

from streamlit_app import fetch_schemes_from_sqlite_db, SchemeEligibilityDeriver, get_tts_audio_data_uri

print("--- EXECUTING MANDATORY END-TO-END TEST SUITE ---")

# TEST 1: BASE DATASET
base_schemes = fetch_schemes_from_sqlite_db({})
print(f"TEST 1 [BASE]: Base scheme count = {len(base_schemes)} (Expected approx 71)")
assert len(base_schemes) >= 50, "Base scheme count must be >= 50"

# TEST 2: CATEGORY (Education & Scholarships)
cat_filters = {"category": "Education & Scholarships"}
cat_schemes = [s for s in base_schemes if SchemeEligibilityDeriver.evaluate_scheme(s, cat_filters)[0]]
print(f"TEST 2 [CATEGORY]: Education & Scholarships count = {len(cat_schemes)} (Expected > 0)")
assert len(cat_schemes) > 0, "Education category count must be > 0"

# TEST 3: GENDER (Female)
gender_filters = {"gender": "Female"}
female_schemes = [s for s in base_schemes if SchemeEligibilityDeriver.evaluate_scheme(s, gender_filters)[0]]
print(f"TEST 3 [GENDER]: Female count = {len(female_schemes)} (Expected > 0)")
assert len(female_schemes) > 0, "Female gender count must be > 0"

# TEST 4: COMBINED ELIGIBILITY (Education & Scholarships + Female)
comb_filters = {"category": "Education & Scholarships", "gender": "Female"}
comb_schemes = [s for s in base_schemes if SchemeEligibilityDeriver.evaluate_scheme(s, comb_filters)[0]]
print(f"TEST 4 [COMBINED]: Education & Scholarships + Female count = {len(comb_schemes)} (Expected > 0)")
assert len(comb_schemes) > 0, "Combined Education + Female count must be > 0"

# TEST 5: STATE + CATEGORY + GENDER (Tamil Nadu + Education & Scholarships + Female)
state_filters = {"state": "Tamil Nadu", "category": "Education & Scholarships", "gender": "Female"}
state_schemes = [s for s in base_schemes if SchemeEligibilityDeriver.evaluate_scheme(s, state_filters)[0]]
print(f"TEST 5 [STATE+CAT+GENDER]: Tamil Nadu + Education + Female count = {len(state_schemes)} (Expected > 0)")
assert len(state_schemes) > 0, "State + Category + Gender count must be > 0"

# TEST 6: RESET FILTERS
empty_filters = {}
reset_schemes = [s for s in base_schemes if SchemeEligibilityDeriver.evaluate_scheme(s, empty_filters)[0]]
print(f"TEST 6 [RESET]: Reset filter count = {len(reset_schemes)} (Expected equals base count {len(base_schemes)})")
assert len(reset_schemes) == len(base_schemes), "Reset must restore full dataset"

# TEST 7: TEXT SEARCH + FILTER
search_schemes = fetch_schemes_from_sqlite_db({"category": "Education & Scholarships", "search": "scholarship"})
search_eval = [s for s in search_schemes if SchemeEligibilityDeriver.evaluate_scheme(s, {"category": "Education & Scholarships"})[0]]
print(f"TEST 7 [TEXT + FILTER]: Search='scholarship' + Category='Education & Scholarships' count = {len(search_eval)}")
assert len(search_eval) > 0, "Text + Category search must return > 0 results"

# TEST 8: VOICE TTS SYNTHESIS (English, Hindi, Tamil)
en_tts = get_tts_audio_data_uri("Hi! Welcome to Scheme Search.", "en")
hi_tts = get_tts_audio_data_uri("नमस्ते! मैं आपकी मदद कर सकता हूं।", "hi")
ta_tts = get_tts_audio_data_uri("வணக்கம்! அரசு திட்டங்களை கண்டுபிடிக்க நான் உதவுகிறேன்.", "ta")

print(f"TEST 8 [VOICE TTS]: English URI len={len(en_tts)}, Hindi URI len={len(hi_tts)}, Tamil URI len={len(ta_tts)}")
assert len(en_tts) > 100, "English TTS must generate valid data URI"
assert len(hi_tts) > 100, "Hindi TTS must generate valid data URI"
assert len(ta_tts) > 100, "Tamil TTS must generate valid data URI"

print("\nALL MANDATORY TESTS PASSED SUCCESSFULLY!")
