from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langchain.messages import HumanMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime
from typing import Any


MAX_MESSAGES = 6


#Trim message from state
@before_model
def trim_msg(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window.

    The kept window always starts at a user message, so a tool call is never
    separated from its tool result (the LLM API rejects orphaned tool messages).
    """
    messages = state["messages"]

    if len(messages) <= MAX_MESSAGES:
        return None

    # Move the cut back to the nearest user message
    start = len(messages) - MAX_MESSAGES
    while start > 0 and not isinstance(messages[start], HumanMessage):
        start -= 1

    if start == 0:
        return None

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *messages[start:]
        ]
    }
