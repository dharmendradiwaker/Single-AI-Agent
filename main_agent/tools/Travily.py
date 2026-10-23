from dotenv import load_dotenv
import getpass
import os
from langchain_tavily import TavilySearch



# Load the APIs 
travily_api =os.getenv("TAVILY_API_KEY")

# Define Tool 
travily_tool = TavilySearch(
    max_results=3,
    include_raw_content=False)
