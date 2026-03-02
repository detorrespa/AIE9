"""State definition for the ARIA multi-agent graph."""

from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ARIAState(TypedDict):
    """State shared across the multi-agent graph."""

    messages: Annotated[list[BaseMessage], add_messages]
    active_agent: str
    question: str
    routing_reason: str
