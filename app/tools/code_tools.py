import re
from pathlib import Path

from app.data.search import search_code as semantic_search_code
from app.data.vector_store import get_collection


REPO_ROOT = Path(
    "/Users/pushpen/Downloads/NewsApp-Clean-Architecture-main"
).resolve()

MAX_FILE_SIZE = 200_000


class CodeTools:

    def __init__(self):
        self.collection = get_collection()

    def _redact_secrets(self, text: str) -> str:
        """
        Redact common secrets before returning repository
        content to the LLM.
        """

        patterns = [
            (
                r'(?i)(api[_-]?key\s*[=:]\s*["\']?)[^"\'\s]+',
                r'\1***REDACTED***',
            ),
            (
                r'(?i)(token\s*[=:]\s*["\']?)[^"\'\s]+',
                r'\1***REDACTED***',
            ),
            (
                r'(?i)(password\s*[=:]\s*["\']?)[^"\'\s]+',
                r'\1***REDACTED***',
            ),
            (
                r'(?i)(secret\s*[=:]\s*["\']?)[^"\'\s]+',
                r'\1***REDACTED***',
            ),
        ]

        for pattern, replacement in patterns:
            text = re.sub(
                pattern,
                replacement,
                text,
            )

        return text
        

    def search_code(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:

        results = semantic_search_code(
            self.collection,
            question,
            top_k=top_k,
        )

        if not results:
            return "No relevant code was found."

        output = []

        for result in results:

            content = self._redact_secrets(
                result["content"]
            )

            output.append(
                f"""
FILE: {result["path"]}
CHUNK: {result["chunk_number"]}

{content}
"""
            )

        return "\n---\n".join(output)

    def read_file(self, path: str) -> str:
        """
        Read a file from the Android repository.

        The requested path must remain inside the repository root.
        """

        requested_path = (
            REPO_ROOT / path
        ).resolve()

        # Guardrail: prevent access outside the repository.
        if not requested_path.is_relative_to(REPO_ROOT):
            return (
                "Access denied: the requested file is "
                "outside the repository."
            )

        if not requested_path.exists():
            return f"File not found: {path}"

        if not requested_path.is_file():
            return f"Not a file: {path}"

        # Guardrail: prevent very large files from entering
        # the LLM context.
        if requested_path.stat().st_size > MAX_FILE_SIZE:
            return (
                f"File is too large to read. "
                f"Maximum size is {MAX_FILE_SIZE} bytes."
            )

        try:
            content = requested_path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:
            return f"Unable to read file as UTF-8: {path}"

        content = self._redact_secrets(content)

        return (
            f"FILE: {path}\n\n"
            f"{content}"
        )

    def find_class(self, class_name: str) -> str:
        """
        Find Kotlin classes, interfaces, objects, or data classes
        matching the requested name.
        """

        matches = []

        for path in REPO_ROOT.rglob("*.kt"):

            try:
                content = path.read_text(
                    encoding="utf-8"
                )

            except UnicodeDecodeError:
                continue

            patterns = [
                rf"\bclass\s+{re.escape(class_name)}\b",
                rf"\binterface\s+{re.escape(class_name)}\b",
                rf"\bobject\s+{re.escape(class_name)}\b",
                rf"\bdata\s+class\s+{re.escape(class_name)}\b",
            ]

            if any(
                re.search(pattern, content)
                for pattern in patterns
            ):
                relative_path = path.relative_to(
                    REPO_ROOT
                )

                matches.append(
                    str(relative_path)
                )

        if not matches:
            return (
                f"No class, interface, or object found "
                f"with name: {class_name}"
            )

        return "\n".join(
            f"FOUND: {path}"
            for path in matches
        )
    

   
    def find_function(self, function_name: str) -> str:
        """
        Find Kotlin function declarations by exact or partial name.
        Accepts multiple candidates separated by |, commas, or semicolons.
        """
        candidates = [
            item.strip().strip("*").strip()
            for item in re.split(r"[|,;]", function_name)
            if item.strip().strip("*").strip()
        ]

        if not candidates:
            return "Please provide a function name to search for."

        matches = []
        declaration_pattern = re.compile(
            r"\bfun\s+(?:<[^>]+>\s*)?([A-Za-z_]\w*)\s*\("
        )

        for path in REPO_ROOT.rglob("*.kt"):
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            for line_number, line in enumerate(content.splitlines(), start=1):
                declaration = declaration_pattern.search(line)
                if not declaration:
                    continue

                declared_name = declaration.group(1)

                exact_match = any(
                    declared_name.lower() == candidate.lower()
                    for candidate in candidates
                )
                partial_match = any(
                    candidate.lower() in declared_name.lower()
                    for candidate in candidates
                )

                if exact_match or partial_match:
                    relative_path = path.relative_to(REPO_ROOT)
                    matches.append(
                        f"FUNCTION: {declared_name}\n"
                        f"FILE: {relative_path}\n"
                        f"LINE: {line_number}\n"
                        f"CODE: {self._redact_secrets(line.strip())}"
                    )

        if not matches:
            return f"No function declaration found for candidates: {candidates}"

        return "\n---\n".join(matches[:50])


    
    def list_files(
        self,
        path: str = ".",
        recursive: bool = False,
        max_entries: int = 100,
    ) -> str:
        """List repository files and directories safely."""

        directory = (REPO_ROOT / path).resolve()

        if not directory.is_relative_to(REPO_ROOT):
            return "Access denied: path is outside the repository."

        if not directory.exists():
            return f"Path not found: {path}"

        if not directory.is_dir():
            return f"Not a directory: {path}"

        excluded = {
            ".git",
            ".gradle",
            ".idea",
            "build",
            ".venv",
            "__pycache__",
        }

        try:
            if recursive:
                entries = (
                    item
                    for item in directory.rglob("*")
                    if not any(part in excluded for part in item.parts)
                )
            else:
                entries = iter(directory.iterdir())

            results = []
            for item in sorted(entries, key=lambda p: str(p).lower()):
                if any(part in excluded for part in item.parts):
                    continue

                relative_path = item.relative_to(REPO_ROOT)
                kind = "DIR " if item.is_dir() else "FILE"
                results.append(f"{kind}: {relative_path}")

                if len(results) >= max(1, min(max_entries, 200)):
                    break

        except OSError as error:
            return f"Unable to list directory: {error}"

        if not results:
            return f"No entries found in: {path}"

        return "\n".join(results)



    
    