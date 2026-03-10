import sys

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.graphs.simple_agent import graph

# Evitar UnicodeEncodeError en consola Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def display_messages(messages, output_file=None):
    lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            line = f"[human] {msg.content}"
        elif isinstance(msg, ToolMessage):
            line = f"[tool] {msg.name}: {msg.content}"
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                calls = ", ".join(tc["name"] for tc in msg.tool_calls)
                line = f"[ai] calling tools: {calls}"
            else:
                line = f"[ai] {msg.content}"
        else:
            line = f"[{msg.type}] {msg.content}"
        lines.append(line)
        if isinstance(msg, ToolMessage):
            print(f"[tool] {msg.name}: {msg.content[:200]}...")
        else:
            print(line)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(lines))
        print(f"\n--- Respuesta guardada en {output_file} ---")


def main():
    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What are the recommended vaccinations for kittens? use retrieve_information tool."
                )
            ]
        }
    )
    display_messages(result["messages"], output_file="rag_response.txt")


if __name__ == "__main__":
    main()
