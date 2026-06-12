import os
import re

from extractor import extract_text
from embedder import embed
from scorer import calculate_similarity
from skill_matcher import load_skills, compare_skills
from explainer import generate_explanation


def extract_relevant_sections(text):
    keywords = [
        "SUMMARY",
        "SKILLS",
        "PROJECTS",
        "EXPERIENCE",
        "CERTIFICATIONS",
        "EDUCATION"
    ]

    lines = text.split("\n")
    collected = []
    capture = False

    for line in lines:
        line = line.strip()

        if line.upper() in keywords:
            capture = True
        elif line.isupper() and line.upper() not in keywords:
            capture = False

        if capture:
            collected.append(line)

    return "\n".join(collected)


def estimate_experience(text):
    patterns = [
        r"(\d+)\+?\s+years",
        r"(\d+)\+?\s+yrs",
        r"experience\s+of\s+(\d+)",
        r"(\d+)\s+year"
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))

    return 0


def count_projects(text):
    keywords = ["project", "projects"]
    count = 0

    for keyword in keywords:
        count += text.lower().count(keyword)

    return count


def education_score(text):
    text = text.lower()

    if "phd" in text:
        return 100
    if "master" in text or "m.tech" in text:
        return 90
    if "bachelor" in text or "b.tech" in text:
        return 80
    if "diploma" in text:
        return 60
    return 40


def certification_score(text):
    keywords = [
        "certified",
        "certificate",
        "certification",
        "aws certified",
        "google cloud",
        "azure"
    ]

    score = 0
    lower = text.lower()

    for word in keywords:
        if word in lower:
            score += 20

    return min(score, 100)


def screen_resume(resume_path, jd_text):
    resume_text = extract_text(resume_path)
    important_text = extract_relevant_sections(resume_text)

    jd_vector = embed(jd_text)
    resume_vector = embed(important_text)

    semantic_score = calculate_similarity(jd_vector, resume_vector)

    skills_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "skills.txt"
        )
    )

    skills = load_skills(skills_path)
    skill_result = compare_skills(jd_text, resume_text, skills)

    required = len(skill_result["matched"]) + len(skill_result["missing"])

    if required == 0:
        skill_score = 0
    else:
        skill_score = (len(skill_result["matched"]) / required) * 100

    years = estimate_experience(resume_text)

    if years >= 5:
        experience_score = 100
    elif years >= 3:
        experience_score = 80
    elif years >= 1:
        experience_score = 60
    else:
        experience_score = 30

    projects = count_projects(resume_text)
    project_score = min(projects * 15, 100)

    education = education_score(resume_text)
    certification = certification_score(resume_text)

    score = round(
        semantic_score * 0.40 +
        skill_score * 0.30 +
        experience_score * 0.10 +
        project_score * 0.10 +
        education * 0.05 +
        certification * 0.05,
        2
    )

    explanation = generate_explanation(score, skill_result["matched"], skill_result["missing"])

    return {
        "score": score,
        "matched": skill_result["matched"],
        "missing": skill_result["missing"],
        "experience": years,
        "projects": projects,
        "education_score": education,
        "certification_score": certification,
        "semantic_score": round(semantic_score, 2),
        "skill_score": round(skill_score, 2),
        "explanation": explanation,
        "resume_text": resume_text
    }


if __name__ == "__main__":
    jd = """
    Looking for a Python Backend Developer
    with FastAPI, Docker,
    AWS and PostgreSQL experience.
    """

    result = screen_resume("../data/uploads/sample_resume.pdf", jd)
    print(result)