"""An agent graph with a post-response vibe check loop.

After the agent responds, a secondary node evaluates if the response has a good vibe
(friendly, natural, appropriate tone). If yes, end; otherwise, loop back to improve.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from app.state import MessagesState
from app.models import get_chat_model
from app.tools import get_tool_belt


class VibeResult(BaseModel):
    good_vibe: bool = Field(
        description="True only if the response is friendly, warm, at least 2-3 sentences, "
        "shows some empathy or personal touch, and is NOT terse, robotic, cold, or raw data."
    )


def _build_model_with_tools():
    """Return a chat model instance bound to the current tool belt."""
    model = get_chat_model()
    return model.bind_tools(get_tool_belt())


def call_model(state: MessagesState) -> dict:
    """Invoke the model with the accumulated messages and append its response."""
    model = _build_model_with_tools()
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


def route_to_action_or_vibe(state: MessagesState):
    """Decide whether to execute tools or run the vibe checker."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "action"
    return "vibe_check"


_vibe_prompt = ChatPromptTemplate.from_template(
    "Evaluate if the final response has a GOOD VIBE. REJECT (good_vibe=false) if ANY of these:\n"
    "- Too short (under ~80 chars or single sentence)\n"
    "- Terse, robotic, or cold tone\n"
    "- Raw data/numbers only, no warmth\n"
    "- Lacks empathy, greeting, or friendly closing\n"
    "- Sounds like a machine or template\n\n"
    "APPROVE (good_vibe=true) only if: friendly, warm, 2+ sentences, shows personal touch.\n\n"
    "Initial Query:\n{initial_query}\n\n"
    "Final Response:\n{final_response}"
)


_MIN_RESPONSE_LENGTH = 80  # Reject responses shorter than this (too terse)


def vibe_check_node(state: MessagesState) -> dict:
    """Evaluate if the latest response has a good vibe (friendly, natural tone)."""
    if len(state["messages"]) > 10:
        return {"messages": [AIMessage(content="VIBE:END")]}

    initial_query = state["messages"][0]
    final_response = state["messages"][-1]
    response_text = getattr(final_response, "content", "") or ""

    # Feedback message so the agent knows what to improve when rejected
    _reject_feedback = (
        "Your previous response was too brief or cold. Please provide a warmer, "
        "more detailed answer with 2-3 sentences and a friendly tone."
    )

    # Auto-reject very short/terse responses
    if len(response_text.strip()) < _MIN_RESPONSE_LENGTH:
        return {
            "messages": [
                HumanMessage(content=_reject_feedback),
                AIMessage(content="VIBE:N"),  # Last msg for vibe_decision routing
            ]
        }

    structured_model = get_chat_model(model_name="gpt-4.1-mini").with_structured_output(VibeResult)
    result = (_vibe_prompt | structured_model).invoke(
        {
            "initial_query": initial_query.content,
            "final_response": final_response.content,
        }
    )

    decision = "Y" if result.good_vibe else "N"
    if decision == "N":
        return {
            "messages": [
                HumanMessage(content=_reject_feedback),
                AIMessage(content="VIBE:N"),  # Last msg for vibe_decision routing
            ]
        }
    return {"messages": [AIMessage(content="VIBE:Y")]}


def vibe_decision(state: MessagesState):
    """Terminate on 'VIBE:Y' or loop otherwise; guard against infinite loops."""
    if any(getattr(m, "content", "") == "VIBE:END" for m in state["messages"][-1:]):
        return END

    last = state["messages"][-1]
    text = getattr(last, "content", "")
    if "VIBE:Y" in text:
        return "end"
    return "continue"


def build_graph():
    """Build an agent graph with an auxiliary vibe check evaluation subgraph."""
    graph = StateGraph(MessagesState)
    tool_node = ToolNode(get_tool_belt())
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    graph.add_node("vibe_check", vibe_check_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        route_to_action_or_vibe,
        {"action": "action", "vibe_check": "vibe_check"},
    )
    graph.add_conditional_edges(
        "vibe_check",
        vibe_decision,
        {"continue": "agent", "end": END, END: END},
    )
    graph.add_edge("action", "agent")
    return graph


graph = build_graph().compile()
