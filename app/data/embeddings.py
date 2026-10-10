from ollama import embed


MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    response = embed(
        model=MODEL,
        input=text,
    )

    return response["embeddings"][0]