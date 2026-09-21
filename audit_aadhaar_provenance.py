import os
import re

search_terms = [
    "aadhaar", "xxxx", "8912", "ramesh", "arun", "profile", "seed", "mock", "dummy", "fixture", "digilocker"
]

results = []

for root, dirs, files in os.walk("."):
    if ".git" in root or "__pycache__" in root or "node_modules" in root or ".venv" in root:
        continue
    for file in files:
        if file.endswith(".py") or file.endswith(".json") or file.endswith(".sql") or file.endswith(".md"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        line_lower = line.lower()
                        for term in search_terms:
                            if term in line_lower:
                                results.append({
                                    "file": path,
                                    "line_num": idx,
                                    "term": term,
                                    "content": line.strip()
                                })
            except Exception as e:
                pass

print(f"Total matching occurrences found: {len(results)}")

# Group by file and term
aadhaar_matches = [r for r in results if "aadhaar" in r["term"] or "8912" in r["term"] or "xxxx" in r["term"]]
print("\n--- AADHAAR & MASKED ID OCCURRENCES ---")
for r in aadhaar_matches:
    print(f"[{r['file']}:L{r['line_num']}] {r['content']}")

user_matches = [r for r in results if "ramesh" in r["term"] or "arun" in r["term"]]
print("\n--- DEMO CITIZEN NAME OCCURRENCES ---")
for r in user_matches:
    print(f"[{r['file']}:L{r['line_num']}] {r['content']}")
