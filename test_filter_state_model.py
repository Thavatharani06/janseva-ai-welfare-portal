import sys
sys.path.insert(0, '.')
from streamlit_app import normalize_filter_value, fetch_schemes_from_sqlite_db

# Simulate UI default values
ui_defaults = {
    "state": "All States / UTs",
    "category": "All Categories",
    "gender": "All",
    "age": "Select",
    "caste": "Select",
    "residence": "Select",
    "benefit": "Select",
    "marital": "Select",
    "disability": "Select",
    "employment": "Select",
    "occupation": "Select"
}

normalized_defaults = {k: normalize_filter_value(v) for k, v in ui_defaults.items()}
print("--- TEST 1: FRESH PAGE LOAD FILTER STATE ---")
print("Normalized defaults:", normalized_defaults)
assert all(v is None for v in normalized_defaults.values()), "All defaults must normalize to None!"

# Simulate User selecting ONLY Category = Education & Scholarships
ui_cat_only = dict(ui_defaults)
ui_cat_only["category"] = "Education & Scholarships"

norm_cat_only = {k: normalize_filter_value(v) for k, v in ui_cat_only.items()}
active_cat_only = {k: v for k, v in norm_cat_only.items() if v is not None}
print("\n--- TEST 2: CATEGORY ONLY SELECTED ---")
print("Active filters:", active_cat_only)
assert active_cat_only == {"category": "Education & Scholarships"}, "Only category should be active!"

res_cat_only = fetch_schemes_from_sqlite_db(active_cat_only)
print(f"Category ONLY result count: {len(res_cat_only)}")
assert len(res_cat_only) > 0, "Category ONLY must return > 0 schemes!"

# Simulate User selecting ONLY Female
ui_female_only = dict(ui_defaults)
ui_female_only["gender"] = "Female"

norm_female_only = {k: normalize_filter_value(v) for k, v in ui_female_only.items()}
active_female_only = {k: v for k, v in norm_female_only.items() if v is not None}
print("\n--- TEST 3: GENDER ONLY SELECTED ---")
print("Active filters:", active_female_only)
assert active_female_only == {"gender": "Female"}, "Only gender should be active!"

res_female_only = fetch_schemes_from_sqlite_db(active_female_only)
print(f"Gender ONLY result count: {len(res_female_only)}")
assert len(res_female_only) > 0, "Gender ONLY must return > 0 schemes!"

print("\nALL FILTER STATE MODEL TESTS PASSED!")
