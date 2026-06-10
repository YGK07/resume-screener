from sentence_transformers import SentenceTransformer

model = None

def get_model():
    global model

    if model is None:
        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    return model

def embed(text):

    model = get_model()

    return model.encode(
        text,
        normalize_embeddings=True
    )

if __name__ == "__main__":

    vec = embed(
        "Python FastAPI Docker AWS"
    )

    print(len(vec))