from langchain.agents import create_agent, AgentState
from model import llm
from tools.Travily import travily_tool
from tools.weather import get_weather
from tools.currancy import currency_converter
from tools.clock import world_clock
from trim_msg import trim_msg
from prompt import prompt
from langgraph.checkpoint.memory import InMemorySaver  



# Agent Executor 
agent = create_agent(
    model=llm,
    tools = [travily_tool, get_weather, world_clock, currency_converter],
    system_prompt = prompt,
    middleware=[trim_msg],
    checkpointer=InMemorySaver(),)