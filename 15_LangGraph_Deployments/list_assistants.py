"""List assistants available from the local LangGraph API."""
from langgraph_sdk import get_sync_client

client = get_sync_client(url="http://localhost:2024")
result = client.assistants.search(limit=20)
print("Assistants disponibles:")
for a in result:
    aid = a.get("assistant_id", a.get("id", "?"))
    name = a.get("name", "?")
    gid = a.get("graph_id", "?")
    print(f"  - {aid}: {name} (graph: {gid})")
