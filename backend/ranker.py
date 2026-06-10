import os

from main import screen_resume


def rank_resumes(folder_path, jd_text):

    results = []

    for file_name in os.listdir(folder_path):

        if file_name.endswith(".pdf"):

            file_path = os.path.join(
                folder_path,
                file_name
            )

            result = screen_resume(
                file_path,
                jd_text
            )

            results.append(
                {
                    "resume": file_name,
                    "score": result["score"]
                }
            )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


if __name__ == "__main__":

    jd = """
    Looking for a Python Backend Developer
    with FastAPI, Docker, AWS and PostgreSQL experience.
    """

    ranked = rank_resumes(
        "../data/uploads",
        jd
    )

    print("\n===== RANKING =====")

    for i, candidate in enumerate(ranked, start=1):

        print(
            f"{i}. {candidate['resume']} - {candidate['score']}%"
        )