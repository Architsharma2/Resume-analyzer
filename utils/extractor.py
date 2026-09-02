import re

def extract_email(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    return emails[0] if emails else "Not found"


def extract_phone(text):
    # Supports Indian and international formats
    patterns = [
        r'\+91[\s\-]?[6-9]\d{9}',
        r'0?[6-9]\d{9}',
        r'\+?\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = re.sub(r'[^\d+]', '', match.group())
            if len(re.sub(r'\D', '', phone)) >= 10:
                return match.group().strip()
    return "Not found"


def extract_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:8]:
        if "@" in line:
            continue
        if re.search(r'\d{10}', line):
            continue
        if len(line) < 3 or len(line) > 40:
            continue
        if re.match(r'^[A-Za-z][A-Za-z\s.\'-]+$', line):
            return line.title()
    return "Not found"


def extract_basic_info(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
    }