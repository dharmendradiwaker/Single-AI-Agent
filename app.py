import os
import streamlit as st
from dotenv import load_dotenv


# Load the APIs
load_dotenv()
missing_keys = [k for k in ("GROQ_API_KEY", "TAVILY_API_KEY", "OPENWEATHER_API_KEY") if not os.getenv(k)]


## Page config
st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="centered")

st.markdown("""
<style>
.app-header {
    padding: 1.4rem 1.6rem;
    border-radius: 16px;
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 55%, #EC4899 100%);
    color: white;
    margin-bottom: 1.2rem;
}
.app-header h1 { color: white; font-size: 1.9rem; margin: 0; padding: 0; }
.app-header p  { color: rgba(255,255,255,0.88); margin: 0.3rem 0 0 0; font-size: 0.98rem; }

.tool-card {
    padding: 0.6rem 0.8rem;
    border-radius: 10px;
    border: 1px solid rgba(99,102,241,0.25);
    background: rgba(99,102,241,0.06);
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
}
.tool-card b { display: block; margin-bottom: 0.1rem; }

.tool-pill {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    margin: 0 0.3rem 0.4rem 0;
    border-radius: 999px;
    background: rgba(99,102,241,0.12);
    color: #6366F1;
    font-size: 0.78rem;
    font-weight: 600;
}
[data-testid="stChatMessage"] { border-radius: 14px; }
</style>
""", unsafe_allow_html=True)


TOOLS = {
    "tavily_search":      ("🔍", "Web search", "News and up-to-date information"),
    "get_weather":        ("🌤️", "Weather", "Current weather for any city"),
    "world_clock":        ("🕒", "World clock", "Local time in any timezone"),
    "currency_converter": ("💱", "Currency", "Latest exchange rates"),
}

EXAMPLES = [
    "What's the weather in Mumbai?",
    "What time is it in New York?",
    "Convert 100 USD to INR",
    "Latest AI news headlines",
]


def tool_pills(tools):
    pills = "".join(
        f'<span class="tool-pill">{TOOLS.get(t, ("🔧",))[0]} {t}</span>' for t in tools
    )
    st.markdown(pills, unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.markdown("### 🧰 Tools")
    for icon, name, desc in TOOLS.values():
        st.markdown(f'<div class="tool-card"><b>{icon} {name}</b>{desc}</div>',
                    unsafe_allow_html=True)

    st.markdown("### 💡 Try asking")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state.pending_prompt = ex

    st.divider()
    show_reasoning = st.toggle("Show model reasoning", value=False)
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_history = []
        st.rerun()

    st.caption("Model: `qwen/qwen3.8-27b` via Groq")


# Header
st.markdown("""
<div class="app-header">
    <h1>🤖 AI Agent</h1>
    <p>Search the web, check the weather, tell the time anywhere, and convert currencies.</p>
</div>
""", unsafe_allow_html=True)

if missing_keys:
    st.error(f"Missing API key(s): {', '.join(missing_keys)}. Add them to your `.env` file and restart the app.")
    st.stop()

from main_agent import agent  # imported after the key check so ChatGroq doesn't fail at import


# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []      # what the UI shows
if "agent_history" not in st.session_state:
    st.session_state.agent_history = [] # full agent state, incl. tool calls and results

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        if msg.get("tools"):
            tool_pills(msg["tools"])
        if show_reasoning and msg.get("reasoning"):
            with st.expander("🧠 Thinking"):
                st.markdown(msg["reasoning"])
        st.markdown(msg["content"])

if not st.session_state.messages:
    st.info("👋 Ask me anything, or pick an example from the sidebar.")


# Agent calling
prompt = st.chat_input("Ask a question...")
if st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    history = st.session_state.agent_history + [{"role": "user", "content": prompt}]

    with st.chat_message("assistant", avatar="🤖"):
        status_box = st.empty()
        reasoning_box = st.expander("🧠 Thinking", expanded=False).empty() if show_reasoning else None
        answer_box = st.empty()

        answer, reasoning, tools_used = "", "", []
        status = None

        try:
            for mode, data in agent.stream({"messages": history}, stream_mode=["messages", "values"]):
                if mode == "values":
                    st.session_state.agent_history = data["messages"]
                    continue

                chunk, meta = data
                if meta.get("langgraph_node") != "model":
                    continue  # skip tool outputs; only show the model's tokens

                for tc in chunk.tool_call_chunks:
                    if tc.get("name"):
                        tools_used.append(tc["name"])
                        if status is None:
                            status = status_box.status("Using tools...", expanded=True)
                        icon = TOOLS.get(tc["name"], ("🔧",))[0]
                        status.write(f"{icon} Calling `{tc['name']}`")

                thinking = chunk.additional_kwargs.get("reasoning_content")
                if thinking:
                    reasoning += thinking
                    if reasoning_box:
                        reasoning_box.markdown(reasoning)

                if chunk.content:
                    answer += chunk.content
                    answer_box.markdown(answer + " ▌")

            if status is not None:
                status.update(label=f"Used {len(tools_used)} tool(s)", state="complete", expanded=False)
            answer_box.markdown(answer or "_No answer returned._")

        except Exception as e:
            if status is not None:
                status.update(label="Tool call failed", state="error")
            answer = f"⚠️ Something went wrong: `{e}`"
            answer_box.error(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "tools": tools_used,
        "reasoning": reasoning,
    })
