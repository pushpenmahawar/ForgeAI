import chromadb


DB_PATH = "./data/chroma"


def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)

    return client.get_or_create_collection(
        name="android_code"
    )


def add_to_collection(
    collection,
    index: list[dict],
):
    for item in index:
        collection.upsert(
            ids=[
                f"{item['path']}::{item['chunk_number']}"
            ],
            embeddings=[item["embedding"]],
            documents=[item["content"]],
            metadatas=[
                {
                    "path": item["path"],
                    "chunk_number": item["chunk_number"],
                }
            ],
        )


def search_collection(
    collection,
    query_embedding: list[float],
    top_k: int = 5,
):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )