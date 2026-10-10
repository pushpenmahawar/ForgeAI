import re


def retrieve(
    question: str,
    files: list[dict],
    top_k: int = 5,
) -> list[dict]:

    words = re.findall(r"\w+", question.lower())

    scored_files = []

    for file in files:
        content = file["content"].lower()

        score = sum(content.count(word) for word in words)

        if score > 0:
            scored_files.append(
                {
                    "path": file["path"],
                    "content": file["content"],
                    "score": score,
                }
            )

    scored_files.sort(
        key=lambda file: file["score"],
        reverse=True,
    )

    return scored_files[:top_k]