import re


def extract_candidate_name(resume_text):
    """
    Attempts to extract the candidate's name from the beginning
    of the resume.
    """

    lines = [
        line.strip()
        for line in resume_text.split("\n")
        if line.strip()
    ]

    # Check only the first few lines
    for line in lines[:5]:

        # Ignore emails
        if "@" in line:
            continue

        # Ignore phone numbers
        if re.search(r"\d{10}", line):
            continue

        # Ignore URLs
        if "linkedin" in line.lower():
            continue

        if "github" in line.lower():
            continue

        if "http" in line.lower():
            continue

        words = line.split()

        if (
            2 <= len(words) <= 4
            and all(word.replace("-", "").isalpha() for word in words)
        ):
            return line.title()

    return "Unknown Candidate"