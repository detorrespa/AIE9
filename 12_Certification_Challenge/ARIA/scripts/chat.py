"""
ARIA — Chat por terminal (testing sin Chainlit).

Uso:
    python scripts/chat.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import AIMessage, HumanMessage
from rich.console import Console
from rich.markdown import Markdown

from aria.agents.orchestrator import graph

console = Console(force_terminal=True)

SESSION_ID = "terminal-session"


def main():
    console.rule("[bold cyan]ARIA -- Chat de prueba[/bold cyan]")
    console.print("Escribe tu pregunta (o 'salir' para terminar).\n")

    while True:
        try:
            query = console.input("[bold blue]Tu:[/bold blue] ")
        except (EOFError, KeyboardInterrupt):
            break

        if query.strip().lower() in ("salir", "exit", "quit"):
            break

        config = {"configurable": {"thread_id": SESSION_ID}}

        with console.status("Pensando..."):
            result = graph.invoke(
                {
                    "messages": [HumanMessage(content=query)],
                    "active_agent": "",
                    "question": query,
                    "routing_reason": "",
                },
                config=config,
            )

        response = result["messages"][-1].content

        console.print()
        console.print(Markdown(response))
        console.print()


if __name__ == "__main__":
    main()
