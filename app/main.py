from ollama import chat

from app.data.search import search_code
from app.data.vector_store import get_collection


MODEL = "qwen2.5:7b-instruct"


collection = get_collection()

print(f"ChromaDB contains {collection.count()} code chunks.")


question = input("\nAsk ForgeAI: ")


# 1. Retrieve relevant code
results = search_code(
    collection,
    question,
    top_k=5,
)


# 2. Build context
context_parts = []

for result in results:
    context_parts.append(
        f"""
--- FILE: {result["path"]} ---
--- CHUNK: {result["chunk_number"]} ---

{result["content"]}
"""
    )

context = "\n".join(context_parts)


# 3. Build RAG prompt
prompt = f"""
You are ForgeAI, an AI assistant specialized in understanding
Android codebases.

Answer the user's question using the repository code provided below.

Rules:
- Use the provided code as your primary source.
- Do not invent files, classes, or behavior.
- If the provided code is insufficient, clearly say so.
- Mention the relevant file names in your answer.

USER QUESTION:
{question}

REPOSITORY CODE:
{context}
"""


# 4. Generate answer
response = chat(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
)


print("\nForgeAI:")
print(response.message.content)