from app.data.embeddings import create_embedding
from app.data.vector_store import search_collection


def search_code(
    collection,
    question: str,
    top_k: int = 5,
) -> list[dict]:

    query_embedding = create_embedding(question)

    results = search_collection(
        collection,
        query_embedding,
        top_k,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    matches = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        matches.append(
            {
                "content": document,
                "path": metadata["path"],
                "chunk_number": metadata["chunk_number"],
                "distance": distance,
            }
        )

    return matches