import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Test query normalization logic
def get_category_terms(cat_str: str):
    if not cat_str:
        return []
    cat_clean = cat_str.strip()
    terms = {cat_clean}
    if "&" in cat_clean:
        terms.add(cat_clean.replace("&", "and"))
    if " and " in cat_clean:
        terms.add(cat_clean.replace(" and ", " & "))
    return list(terms)

print("Terms for 'Housing & Urban Development':", get_category_terms("Housing & Urban Development"))
print("Terms for 'Housing and Urban Development':", get_category_terms("Housing and Urban Development"))
print("Terms for 'Women & Child Development':", get_category_terms("Women & Child Development"))
