from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from model import llm
from tools.search import search_tool
from tools.weather import get_weather
from tools.currency import currency_converter
from tools.clock import world_clock
from trim_msg import trim_msg
from prompt import prompt


# Agent Executor
agent = create_agent(
    model=llm,
    tools=[search_tool, get_weather, world_clock, currency_converter],
    system_prompt=prompt,
    middleware=[trim_msg],
    checkpointer=InMemorySaver(),)
