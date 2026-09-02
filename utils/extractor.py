import re

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

def extract_phone(text):
    # Works for Indian and international formats
    patterns = [
        r'(?:\+91[\-\s]?)?[6-9]\d{9}',
        r'(?:\+?\d{1,3}[\-\s]?)?\(?\d{2,4}\)?[\-\s]?\d{3,4}[\-\s]?\d{4}',
        r'\b\d{10}\b',
        r'\b\d{3}[\-\s]\d{3}[\-\s]\d{4}\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return "Not found"

def extract_name(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:8]:
        if "@" in line or re.search(r'\d{5,}', line):
            continue
        if 2 <= len(line.split()) <= 5 and len(line) < 50:
            return line.title()
    return "Not found"

def extract_basic_info(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text)
    }