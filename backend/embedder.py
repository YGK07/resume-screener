from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/all-mpnet-base-v2"
)

def embed(text):
    return model.encode(
        text,
        normalize_embeddings=True
    )

if __name__ == "__main__":

    jd = """
    Looking for a Python Backend Developer
    with FastAPI and Docker experience
    """

    vec = embed(jd)

    print("Vector Length:", len(vec))
    print(vec[:10])