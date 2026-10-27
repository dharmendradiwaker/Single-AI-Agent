# Single Agent — LangChain Tool-Calling Assistant

> **Live demo:** _add your Streamlit Cloud link here_

<!-- Add a screenshot or GIF of the app: ![Demo](demo.gif) -->

An AI assistant, with both a **Streamlit web app** and a command-line interface, built with **LangChain** and **LangGraph** that can search the web, check the weather, tell the time anywhere in the world, and convert currencies. It runs on a Qwen model served by **Groq** and streams its reasoning, tool calls, and answers in real time.

---

## Features

| Tool | What it does | Data source |
|---|---|---|
| `tavily_search` | Searches the web for news and up-to-date information (top 3 results) | [Tavily](https://tavily.com) |
| `get_weather` | Current weather, temperature (°C), pressure, and humidity for a city | [OpenWeatherMap](https://openweathermap.org/api) |
| `world_clock` | Current local time for any IANA timezone (e.g. `Asia/Kolkata`) | Python `zoneinfo` (no API needed) |
| `currency_converter` | Converts an amount between currencies using the latest exchange rates | [Frankfurter](https://frankfurter.dev) (free, no key) |

- **Rich Streamlit UI**: animated hero, clickable starter cards, live step-by-step tool status, typing indicator, and response time per answer
- **Visual tool result cards**: weather card (colour changes with conditions and day/night), currency conversion card, digital world clock, and news cards with site icons
- **Short-term memory**: follow-up questions like "and in euros?" use earlier context (web app and CLI)
- **Context trimming**: older messages are dropped automatically so long chats stay within the model's context window
- **Demo-safe**: per-session question limit and a friendly message when the LLM is rate limited
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
5. An `InMemorySaver` checkpointer stores the conversation per `thread_id`, and the `trim_msg` middleware runs before every model call to keep only the most recent messages. The cut always starts at a user message, so a tool call is never separated from its result.

---

## Project Structure

```
main_agent/
├── app.py              # Streamlit web app (chat flow and streaming)
├── ui.py               # UI styles, hero, starter cards and tool result cards
├── main.py             # Interactive command-line chat
├── agent.py            # Builds the agent (model + tools + prompt + memory + trimming)
├── model.py            # Groq LLM setup
├── prompt.py           # System prompt (tool-routing instructions)
├── trim_msg.py         # Middleware that trims old messages before each model call
├── config.py           # Thread id used by the CLI
├── tools/
│   ├── search.py       # Tavily web search
│   ├── weather.py      # OpenWeatherMap
│   ├── clock.py        # World clock (zoneinfo)
│   └── currency.py     # Frankfurter currency converter
├── .streamlit/
│   └── config.toml     # Streamlit theme
├── .env.example        # Template for your API keys
└── requirements.txt    # Python dependencies
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>/main_agent
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

Copy `.env.example` to `.env` inside `main_agent/` and fill in your keys:

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

Then open http://localhost:8501 in your browser. Click a starter card or type a question. The sidebar has:
- the list of available tools
- how many demo questions this session has used
- **Show model reasoning** and **Show tool result cards** toggles
- a **New chat** button that starts a fresh conversation

### Command line

```bash
python main.py
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

| Setting | Location | Default |
|---|---|---|
| LLM model | `MODEL_NAME` in `model.py` | `qwen/qwen3.8-27b` |
| Temperature | `ChatGroq(temperature=...)` in `model.py` | `0` (deterministic) |
| Search results | `TavilySearch(max_results=...)` in `tools/search.py` | `3` |
| System prompt | `prompt` in `prompt.py` | Short, tool-routing instructions |
| Memory window | `MAX_MESSAGES` in `trim_msg.py` | `6` messages |
| Web app question limit | `MAX_QUESTIONS_PER_SESSION` env var | `20` per browser session |

### Adding a new tool

1. Write a Python function and decorate it with `@tool`.
2. Give it a clear docstring; the LLM uses it to decide when to call the tool.
3. Save it in `tools/` and add it to the `tools=[...]` list in `agent.py`.
4. Optionally mention it in the system prompt.

```python
@tool
def my_tool(arg: str):
    """Describe what this tool does and when to use it."""
    ...
```

---

## Deploy (Streamlit Community Cloud)

1. Push the repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app and set the main file path to `main_agent/app.py`.
3. Under **Advanced settings → Secrets**, add your keys (they become environment variables):
   ```toml
   GROQ_API_KEY = "..."
   TAVILY_API_KEY = "..."
   OPENWEATHER_API_KEY = "..."
   MAX_QUESTIONS_PER_SESSION = "20"
   ```
4. Deploy and share the link.

---

## Notes & Limitations

- **Short-term memory only**: conversations live in memory and are lost when the app restarts. Only the last few messages are kept, so the agent remembers roughly the last one or two turns.
- **Question limit is per browser session**: refreshing the page starts a new session. It stops casual overuse, not a determined abuser.
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
