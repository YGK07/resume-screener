import os

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
        "CERTIFICATIONS"
    ]

    lines = text.split("\n")

    collected = []

    capture = False

    for line in lines:

        line = line.strip()

        if line.upper() in keywords:
            capture = True

        elif (
            line.isupper()
            and line.upper() not in keywords
        ):
            capture = False

        if capture:
            collected.append(line)

    return "\n".join(collected)


def screen_resume(
    resume_path,
    jd_text
):

    # Extract Resume Text
    resume_text = extract_text(
        resume_path
    )

    print("\nResume Text Preview:")
    print(resume_text[:500])

    # Extract Important Sections
    important_text = extract_relevant_sections(
        resume_text
    )

    print("\n=== IMPORTANT SECTIONS ===")
    print(important_text[:1000])

    # Generate Embeddings
    jd_vector = embed(
        jd_text
    )

    resume_vector = embed(
        important_text
    )

    # Semantic Similarity
    semantic_score = calculate_similarity(
        jd_vector,
        resume_vector
    )

    # Load Skills Database (Cloud-Safe Path)
    skills_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "skills.txt"
        )
    )

    skills = load_skills(
        skills_path
    )

    # Skill Analysis
    skill_result = compare_skills(
        jd_text,
        resume_text,
        skills
    )

    required_skills = (
        len(skill_result["matched"])
        + len(skill_result["missing"])
    )

    if required_skills > 0:

        skill_score = (
            len(skill_result["matched"])
            / required_skills
        ) * 100

    else:

        skill_score = 0

    # Final Weighted Score
    score = round(
        (semantic_score * 0.7)
        + (skill_score * 0.3),
        2
    )

    print(f"\nSemantic Score: {semantic_score:.2f}")
    print(f"Skill Score: {skill_score:.2f}")
    print(f"Final Score: {score:.2f}")

    # AI Explanation
    explanation = generate_explanation(
        score,
        skill_result["matched"],
        skill_result["missing"]
    )

    return {
        "score": score,
        "matched": skill_result["matched"],
        "missing": skill_result["missing"],
        "explanation": explanation
    }


if __name__ == "__main__":

    jd = """
    Looking for a Python Backend Developer
    with FastAPI, Docker, AWS and
    PostgreSQL experience.
    """

    result = screen_resume(
        "../data/uploads/sample_resume.pdf",
        jd
    )

    print("\n===== RESUME SCREENING RESULT =====")
    print(f"Match Score: {result['score']}%")
    print(f"Matched Skills: {result['matched']}")
    print(f"Missing Skills: {result['missing']}")
    print("\nExplanation:")
    print(result["explanation"])
    print("==================================")