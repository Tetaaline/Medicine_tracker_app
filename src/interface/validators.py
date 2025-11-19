import re
from datetime import datetime

VALID_DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

def is_letters_only(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z ]+", text))

def is_alnum_username(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9]+", text))

def is_valid_dosage(text: str) -> bool:
    return bool(re.fullmatch(r"\d+(\.\d+)?\s?(mg|g|l)", text, flags=re.IGNORECASE))

def is_valid_time_hms(text: str) -> bool:
    try:
        datetime.strptime(text, "%H:%M:%S")
        return bool(re.fullmatch(r"\d{2}:\d{2}:\d{2}", text))
    except ValueError:
        return False

def normalize_days(days_list):
    out = []
    for d in days_list:
        d = d.strip().title()[:3]
        if d in VALID_DAYS:
            out.append(d)
    seen = set()
    res = []
    for d in out:
        if d not in seen:
            seen.add(d); res.append(d)
    return res

