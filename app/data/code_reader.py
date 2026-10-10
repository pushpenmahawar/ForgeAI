from pathlib import Path


def read_kotlin_files(repo_path: str) -> list[dict]:
    repo = Path(repo_path)

    files = []

    for path in repo.rglob("*.kt"):
        try:
            content = path.read_text(encoding="utf-8")

            files.append(
                {
                    "path": str(path.relative_to(repo)),
                    "content": content,
                }
            )

        except UnicodeDecodeError:
            continue

    return files