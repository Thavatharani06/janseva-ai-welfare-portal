import json
import os

json_path = os.path.join("backend", "data", "myscheme_dataset", "schemes.json")
if not os.path.exists(json_path):
    json_path = os.path.join("data", "myscheme_dataset", "schemes.json")

with open(json_path, "r", encoding="utf-8") as f:
    schemes = json.load(f)

print(f"Total schemes in {json_path}: {len(schemes)}")

# Check keys of first item
print("Keys of first scheme:", list(schemes[0].keys()))

# Search for PMAY-U in schemes.json
pmay = [s for s in schemes if "PMAY" in s.get("code", "") or "PMAY" in s.get("title", "") or "Awas" in s.get("title", "")]
print(f"Found {len(pmay)} PMAY schemes in JSON:")
for p in pmay:
    print("  Code:", p.get("code"))
    print("  Title:", p.get("title"))
    print("  'category' key:", repr(p.get("category")))
    print("  'category_name' key:", repr(p.get("category_name")))
    print("  'category_id' key:", repr(p.get("category_id")))
    print("---")

# Distinct values of 'category' in schemes.json
categories_in_json = set(s.get("category") for s in schemes)
print("Distinct 'category' values in schemes.json:")
for c in sorted(list(categories_in_json), key=lambda x: str(x)):
    print(" ", repr(c))
