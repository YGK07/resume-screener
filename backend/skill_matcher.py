import re


def load_skills(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def extract_skills(text, skill_database):

    text = text.lower()

    found_skills = set()

    for skill in skill_database:
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", text):
            found_skills.add(skill)

    return found_skills


def compare_skills(jd_text, resume_text, skill_database):

    jd_skills = extract_skills(
        jd_text,
        skill_database
    )

    resume_skills = extract_skills(
        resume_text,
        skill_database
    )

    matched = jd_skills.intersection(
        resume_skills
    )

    missing = jd_skills - resume_skills

    return {
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing))
    }


if __name__ == "__main__":

    skills = load_skills("../data/skills.txt")

    jd = """
    Python FastAPI Docker AWS PostgreSQL
    """

    resume = """
    Python FastAPI Docker
    """

    result = compare_skills(
        jd,
        resume,
        skills
    )

    print(result)