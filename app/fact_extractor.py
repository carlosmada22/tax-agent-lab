import re


def extract_facts(text: str) -> dict:
    t = text.strip()
    facts = {}

    # Age: "I'm 50", "I am 50", "age 50"
    m = re.search(r"\b(i[' ]?m|i am|age)\s+(\d{1,3})\b", t, re.IGNORECASE)
    if m:
        facts["age"] = int(m.group(2))

    # Residency: very simple keyword detection
    if re.search(r"\bgermany\b|\bdeutschland\b", t, re.IGNORECASE):
        facts["residency"] = "DE"

    # Employment
    if re.search(r"\bself[- ]?employed\b|\bfreelancer\b", t, re.IGNORECASE):
        facts["employment"] = "self_employed"
    elif re.search(r"\bemployee\b|\bsalaried\b", t, re.IGNORECASE):
        facts["employment"] = "employee"

    return facts
