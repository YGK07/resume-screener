from sklearn.metrics.pairwise import cosine_similarity
from embedder import embed


def calculate_similarity(vec1, vec2):
    score = cosine_similarity(
        [vec1],
        [vec2]
    )[0][0]

    return round(score * 100, 2)


if __name__ == "__main__":

    jd = """
    Looking for a Python Backend Developer
    with FastAPI and Docker experience
    """

    resume = """
    Experienced Java Spring Boot Developer
    with expertise in Microservices
    """

    jd_vec = embed(jd)
    resume_vec = embed(resume)

    score = calculate_similarity(
        jd_vec,
        resume_vec
    )

    print(f"Match Score: {score}%")