import json
import re
from collections import defaultdict

user, mod, want = "", "", 0
offers = defaultdict(lambda: defaultdict(lambda: [set(), set()]))
re_module = r"([A-Z]{2}\d{4})"
re_index = r"\b(\d{5})\b"
re_index_range = r"(\d{5})(?:\s?[-–—]| to )\s?(\d{5})"
# Captures days and timeslots (e.g., Mon 1030-1220) [cite: 1, 3]
re_time = r"((?:Mon|Tue|Wed|Thu|Fri|Monday|Tuesday|Wednesday|Thursday|Friday)\b.*?\d{2,4}[-\s:]{1,3}(?:to\s)?\d{2,4})"


def get_index_range(start_str: str, end_str: str) -> set[str]:
    start, end = int(start_str), int(end_str)
    return set(str(i).zfill(5) for i in range(start, end + 1))


def extract_indices(line: str) -> set[str]:
    found = set()
    ranges = re.findall(re_index_range, line)
    for start, end in ranges:
        found |= get_index_range(start, end)

    all_singles = re.findall(re_index, line)
    found |= set(all_singles)
    return found


with open("messages.json", "r", encoding="utf-8") as f:
    messages = json.load(f)

for msg in messages:
    user = msg["sender"]
    lines = msg["content"].split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        module_match = re.search(re_module, line, re.IGNORECASE)
        if module_match:
            mod = module_match.group(1).upper()
        if "have" in line.lower():
            want = 0
        elif "want" in line.lower():
            want = 1
        indices = extract_indices(line)
        offers[user][mod][want] |= indices

[print(o) for o in offers.items()]
