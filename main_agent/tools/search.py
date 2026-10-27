from dotenv import load_dotenv
from langchain_tavily import TavilySearch


# Load the APIs (TavilySearch reads TAVILY_API_KEY from the environment)
load_dotenv()

# Define Tool
search_tool = TavilySearch(
    max_results=3,
    include_raw_content=False)
