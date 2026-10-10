from pathlib import Path


def chunk_code(
    content: str,
    chunk_size: int = 80,
    overlap: int = 20,
) -> list[str]:
    lines = content.splitlines()

    chunks = []

    start = 0

    while start < len(lines):
        end = min(start + chunk_size, len(lines))

        chunk = "\n".join(lines[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(lines):
            break

        start = end - overlap

    return chunks