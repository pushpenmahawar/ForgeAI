from app.data.code_reader import read_kotlin_files
from app.data.embeddings import create_embedding
from app.data.chunker import chunk_code


def create_index(repo_path: str) -> list[dict]:
    files = read_kotlin_files(repo_path)

    index = []

    for file in files:
        chunks = chunk_code(file["content"])

        print(
            f"{file['path']} -> "
            f"{len(chunks)} chunks"
        )

        for chunk_number, chunk in enumerate(chunks):
            embedding = create_embedding(chunk)

            index.append(
                {
                    "path": file["path"],
                    "chunk_number": chunk_number,
                    "content": chunk,
                    "embedding": embedding,
                }
            )

    return index