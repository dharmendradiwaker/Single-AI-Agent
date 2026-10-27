from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load the APIs (ChatGroq reads GROQ_API_KEY from the environment)
load_dotenv()

MODEL_NAME = "qwen/qwen3.8-27b"

## Initialize the llm Model
llm = ChatGroq(
    model=MODEL_NAME,
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2
)
