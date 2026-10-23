import getpass
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load the APIs 
load_dotenv()
GROQ_API_KEY = os.getenv("Groq_API")


## Initialize the llm Model
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2
)