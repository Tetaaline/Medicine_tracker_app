import re
from datetime import datetime

VALID_DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

def is_letters_only(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z ]+", text))

def is_alnum_username(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9]+", text))

def is_valid_dosage(text: str) -> bool:
    return bool(re.fullmatch(r"\d+(\.\d+)?\s?(mg|g|l)", text, flags=re.IGNORECASE))
