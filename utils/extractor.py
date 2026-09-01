import re

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

def extract_phone(text):
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    if phones:
        # Join the groups if needed
        return "".join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
    return "Not found"

def extract_basic_info(text):
    email = extract_email(text)
    phone = extract_phone(text)
    return {
        "email": email,
        "phone": phone
    }