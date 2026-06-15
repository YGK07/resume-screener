import re


def extract_email(text):
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )
    return match.group(0) if match else "Not Found"


def extract_phone(text):
    match = re.search(
        r"(\+?\d[\d\s\-]{8,}\d)",
        text
    )
    return match.group(0) if match else "Not Found"


def extract_linkedin(text):
    match = re.search(
        r"https?://(?:www\.)?linkedin\.com/\S+",
        text
    )
    return match.group(0) if match else "Not Found"


def extract_github(text):
    match = re.search(
        r"https?://(?:www\.)?github\.com/\S+",
        text
    )
    return match.group(0) if match else "Not Found"