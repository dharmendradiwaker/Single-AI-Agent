# Single Agent — LangChain Tool-Calling Assistant

An AI assistant, with both a **Streamlit web app** and a command-line interface, built with **LangChain** and **LangGraph** that can search the web, check the weather, tell the time anywhere in the world, and convert currencies. It runs on a Qwen model served by **Groq** and streams its reasoning, tool calls, and answers in real time.

---

## Features

| Tool | What it does | Data source |
|---|---|---|
| `tavily_search` | Searches the web for news and up-to-date information (top 3 results) | [Tavily](https://tavily.com) |
| `get_weather` | Current weather, temperature (°C), pressure, and humidity for a city | [OpenWeatherMap](https://openweathermap.org/api) |
| `world_clock` | Current local time for any IANA timezone (e.g. `Asia/Kolkata`) | Python `zoneinfo` (no API needed) |
| `currency_converter` | Converts an amount between currencies using the latest exchange rates | [Frankfurter](https://frankfurter.dev) (free, no key) |

- **Streamlit web UI**: chat interface with example prompts, live tool-call status, and a clear-chat button
- **Conversation memory (web app)**: follow-up questions like "and in euros?" use earlier context
- **Streaming output**: prints tokens as they're generated
- **Visible reasoning**: shows the model's thinking separately from its answer
- **Tool call tracing**: prints `🔧 calling <tool>` whenever the agent uses a tool

---

## How It Works

The agent is created with LangChain's `create_agent`, which builds a LangGraph **ReAct loop**:

```
        ┌──────────────┐
User ──▶│  model node  │──▶ Final answer
        └──────┬───────┘
               │ tool call?
               ▼
        ┌──────────────┐
        │  tools node  │  (search / weather / clock / currency)
        └──────┬───────┘
               │ tool result
               └──────▶ back to model node
```

1. The LLM reads the user's question and the system prompt.
2. It decides whether to answer directly or call one of the tools (based on each tool's docstring).
3. Tool results are fed back to the LLM, which can call more tools or produce the final answer.
4. Only the output of the `model` node is printed, so raw tool responses stay hidden.

---

## Project Structure

```
single-agent/
├── app.py              # Streamlit web app (imports the agent from main_agent.py)
├── main_agent.py       # Agent, tools, and interactive CLI loop
├── .streamlit/
│   └── config.toml     # Streamlit theme
├── test_agent.ipynb    # Notebook for experimenting with the agent
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

Create a `.env` file in the project folder:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
```

| Key | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) |
| `OPENWEATHER_API_KEY` | [home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys) |

> `.env` is listed in `.gitignore`, so your keys won't be committed.

---

## Usage

### Web app (Streamlit)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser. The sidebar has:
- the list of available tools
- example questions you can click to send
- a **Show model reasoning** toggle
- a **Clear chat** button that starts a new conversation

### Command line

```bash
python main_agent.py
```

Type a question at the prompt. Type `exit`, `stop`, or `q` to quit.

### Example questions

```
Ask question:- What's the weather in Mumbai?
Ask question:- What time is it in New York right now?
Ask question:- Convert 250 USD to INR
Ask question:- What is the EUR to GBP exchange rate?
Ask question:- What are today's top tech news headlines?
```

### Example output

```
Ask question:- Convert 100 USD to INR

🔧 calling currency_converter
100 USD is about 9,482 INR (rate as of 2026-10-22).
```

---

## Configuration

You can tweak the agent in `main_agent.py`:

| Setting | Location | Default |
|---|---|---|
| LLM model | `ChatGroq(model=...)` | `qwen/qwen3.8-27b` |
| Temperature | `ChatGroq(temperature=...)` | `0` (deterministic) |
| Search results | `TavilySearch(max_results=...)` | `3` |
| System prompt | `prompt` variable | Short, tool-routing instructions |

### Adding a new tool

1. Write a Python function and decorate it with `@tool`.
2. Give it a clear docstring; the LLM uses it to decide when to call the tool.
3. Add it to the `tools=[...]` list in `create_agent(...)`.
4. Optionally mention it in the system prompt.

```python
@tool
def my_tool(arg: str):
    """Describe what this tool does and when to use it."""
    ...
```

---

## Notes & Limitations

- **No conversation memory in the CLI**: each question in `main_agent.py` is handled independently (the web app keeps history for the session). To add memory, pass a `checkpointer` (e.g. `InMemorySaver`) to `create_agent` and a `thread_id` in the config.
- **Exchange rates** come from the European Central Bank via Frankfurter and update once per working day; they are reference rates, not live market prices.
- **Timezones** must be valid IANA names (`Europe/London`, not `London`). The LLM usually maps city names correctly.

---

## Tech Stack

- [Streamlit](https://streamlit.io/) (web UI)
- [LangChain](https://python.langchain.com/) / [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Groq](https://groq.com/) (LLM inference)
- [Tavily](https://tavily.com/) (web search)
- [OpenWeatherMap](https://openweathermap.org/) (weather)
- [Frankfurter](https://frankfurter.dev/) (currency rates)
