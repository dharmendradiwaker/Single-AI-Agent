import getpass
import os
from langchain_groq import ChatGroq
from langchain.agents import create_agent
import urllib.request
from langchain.tools import tool
from langchain_tavily import TavilySearch
from langchain_core.prompts import PromptTemplate
import requests
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo


# Load the APIs 
load_dotenv()
GROQ_API_KEY = os.getenv("Groq_API")
travily_api =os.getenv("TAVILY_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


## Initialize the llm Model
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2
)


# Define Tool 
travily_tool = TavilySearch(
    max_results=3,
    include_raw_content=False)


# Custom weather api tool
@tool
def get_weather(city):

    """ 
    Search and get the weather data of any city.

    Args: 
        city: which city weather you want to find
    """

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    data = requests.get(url, params=params)
    try:
        if data.status_code:
            data = data.json()

            weather = data['weather'][0]['main']
            Temp = data['main']['temp']
            Pressure = data['main']['pressure']
            humidity = data['main']['humidity']

            data = {"weather": weather,
                    "temp": Temp,
                    "Pressure": Pressure,
                    "humidity": humidity}
            return data
    except:
        return f"Get Weather tool unable to fetch the weather data"


@tool
def world_clock(timezone):
    """
    Get the current local time in a specific IANA timezone

    Use this whenever a user asks what time it is in a specific city or region.
    The timezone argument must be a valid IANA timezone name (e.g., 'America/New_York', 'Asia/Kolkata', 'Europe/London').
    """

    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)

        return now.strftime("Current time in %Z (%z): %Y-%m-%d %H:%M:%S")
    except Exception as e:
        return (
            f"Invalid timezone '{timezone}'. Please use a valid IANA timezone name."
        )


@tool
def currency_converter(amount: float, from_currency: str, to_currency: str):
    """
    Convert an amount from one currency to another using the latest exchange rates.

    Use this whenever the user asks to convert money or asks for an exchange rate.

    Args:
        amount: the amount of money to convert (use 1 to just get the exchange rate)
        from_currency: 3-letter ISO currency code to convert from (e.g., 'USD', 'EUR', 'INR')
        to_currency: 3-letter ISO currency code to convert to (e.g., 'USD', 'EUR', 'INR')
    """

    url = "https://api.frankfurter.dev/v1/latest"
    params = {"amount": amount,
              "from": from_currency.upper(),
              "to": to_currency.upper()}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return f"Currency conversion failed: {resp.json().get('message', resp.text)}"

        data = resp.json()
        converted = data['rates'][to_currency.upper()]

        return {"amount": data['amount'],
                "from": data['base'],
                "to": to_currency.upper(),
                "converted_amount": converted,
                "rate_date": data['date']}
    except Exception:
        return "Currency converter tool unable to fetch the exchange rate"



#Prompt Define
prompt = """You are a helpful assistant.
- Use get_weather when the user asks about current weather in a city.
- Use currency_converter for every currency conversion or exchange rate question, including follow-ups. Never guess exchange rates.
- Use world_clock when the user asks for the current time somewhere.
- Use the search tool for news or other up-to-date information.
- If no tool is needed, answer directly.
Keep answers short and clear."""


# Agent Executor 
agent = create_agent(
    model=llm,
    tools = [travily_tool, get_weather, world_clock, currency_converter],
    system_prompt = prompt
)


#Agent calling
def main():
    while True:
        q = input("\n\nAsk question:- ")
        if q in ("exit","stop", "q"):
            break
        query_resp = agent.stream({"messages":[{"role":"user", "content":q}]},stream_mode="messages")

        for chunk, meta in query_resp:
            if meta.get("langgraph_node") != "model":
                continue  # skip tool outputs; only show the model's tokens

            thinking = chunk.additional_kwargs.get("reasoning_content")
            if thinking:
                print(thinking, end="", flush=True)

            if chunk.content:
                print(chunk.content, end="", flush=True)

            for tc in chunk.tool_call_chunks:
                if tc.get("name"):
                    print(f"\n🔧 calling {tc['name']}", flush=True)







if __name__ == "__main__":
    main()

