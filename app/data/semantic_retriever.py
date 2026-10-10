import numpy as np

from app.data.embeddings import create_embedding


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    a = np.array(vector_a)
    b = np.array(vector_b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def retrieve(
    question: str,
    index: list[dict],
    top_k: int = 5,
) -> list[dict]:

    question_embedding = create_embedding(question)

    results = []

    for item in index:
        similarity = cosine_similarity(
            question_embedding,
            item["embedding"],
        )

        results.append(
            {
                "path": item["path"],
                "chunk_number": item["chunk_number"],
                "content": item["content"],
                "score": similarity,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]