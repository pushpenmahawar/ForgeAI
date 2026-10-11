from ollama import chat

from app.tools.tool_registry import ToolRegistry


MODEL = "qwen2.5:7b-instruct"



SYSTEM_PROMPT = """
You are ForgeAI, an AI assistant that understands Android and Kotlin codebases.

You have tools to search code, read files, find classes, and find functions.

Rules:
1. For questions about the repository, use tools to inspect the actual source code.
2. Never invent function names, class names, file paths, or implementation details.
3. When tracing a feature, follow the code path across layers instead of stopping at the first match.
4. For a repository method, identify:
   - The repository interface.
   - The concrete implementation, often named with an Impl suffix.
   - The API service or data source called by that implementation.
   - The ViewModel or caller, when relevant.
5. Use find_function with a likely function name. If uncertain, use a short list of candidates separated by |, such as:
   getTopHeadlines|fetchNews
   Do not pass wildcard patterns as if they were supported search syntax.
6. Use find_class to locate a class or interface, then read_file to inspect its source.
7. Use search_code when you need semantic search to discover relevant code.
8. After receiving tool results, use the actual names and paths found in those results for subsequent tool calls.
9. If a tool returns no matches, try a more suitable search rather than repeating the same failed query.
10. Clearly distinguish verified findings from assumptions. If you cannot verify something, say so.
11. Keep answers concise and cite relevant repository file paths.
"""


registry = ToolRegistry()

tools = registry.get_tools()
tool_map = registry.get_tool_map()


question = input("Ask ForgeAI: ")


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": question,
    },
]



MAX_TURNS = 8

for turn in range(MAX_TURNS):
    response = chat(
        model=MODEL,
        messages=messages,
        tools=tools,
    )

    messages.append(response.message)

    if not response.message.tool_calls:
        print("\nForgeAI:")
        print(response.message.content or "No final answer was generated.")
        break

    for tool_call in response.message.tool_calls:
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments or {}

        print(f"\n[Tool Call] {tool_name}")
        print(f"[Arguments] {arguments}")

        function = tool_map.get(tool_name)

        if function is None:
            result = f"Unknown tool: {tool_name}"
        else:
            try:
                result = function(**arguments)
                result = str(result)
            except Exception as error:
                result = (
                    f"Tool execution failed for {tool_name}: "
                    f"{type(error).__name__}: {error}"
                )

        print("[Tool Result]")
        print(result)

        messages.append(
            {
                "role": "tool",
                "tool_name": tool_name,
                "content": result,
            }
        )
else:
    print(
        f"\nForgeAI stopped after reaching the "
        f"{MAX_TURNS}-turn limit."
    )
