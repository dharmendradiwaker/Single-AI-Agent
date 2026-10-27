import os
import time
import uuid
import streamlit as st
from dotenv import load_dotenv
from groq import RateLimitError
import ui
from trim_msg import MAX_MESSAGES


# Load the APIs
load_dotenv()
missing_keys = [k for k in ("GROQ_API_KEY", "TAVILY_API_KEY", "OPENWEATHER_API_KEY") if not os.getenv(k)]

# Cap questions per browser session so a public demo can't drain the API quotas
MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS_PER_SESSION", "20"))
MODEL_LABEL = "Qwen3.8 27B"


## Page config
st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="centered")
st.markdown(ui.CSS, unsafe_allow_html=True)


# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []      # what the UI shows
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())  # agent memory lives in the checkpointer under this id
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0  # not reset by "Clear chat"


# Sidebar
with st.sidebar:
    ui.sidebar_brand()

    st.markdown('<div class="side-title">Session</div>', unsafe_allow_html=True)
    used = st.session_state.questions_asked
    st.progress(min(used / MAX_QUESTIONS, 1.0), text=f"{used} / {MAX_QUESTIONS} questions used")

    show_reasoning = st.toggle("🧠 Show model reasoning", value=False)
    show_cards = st.toggle("🎴 Show tool result cards", value=True)
    if st.button("🗑️ New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())  # new thread = fresh agent memory
        st.rerun()

    st.markdown('<div class="side-foot">Built with LangChain · LangGraph · Groq · Streamlit</div>',
                unsafe_allow_html=True)


# Header
ui.hero(MODEL_LABEL, MAX_MESSAGES)

if missing_keys:
    st.error(f"Missing API key(s): {', '.join(missing_keys)}. Add them to your `.env` file and restart the app.")
    st.stop()

from agent import agent  # imported after the key check so ChatGroq doesn't fail at import

config = {"configurable": {"thread_id": st.session_state.thread_id}}


# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        if msg.get("tools"):
            ui.tool_pills(msg["tools"])
        if show_cards:
            for name, content in msg.get("results", []):
                ui.tool_card(name, content)
        if show_reasoning and msg.get("reasoning"):
            with st.expander("🧠 Thinking"):
                st.markdown(msg["reasoning"])
        st.markdown(msg["content"])
        if msg.get("elapsed") is not None:
            ui.meta_row(msg["elapsed"], len(msg.get("tools", [])))

prompt = None
if not st.session_state.messages:
    ui.welcome()
    prompt = ui.example_cards()


# Agent calling
typed = st.chat_input("Ask about weather, time, currency or the news...")
prompt = typed or prompt

if prompt and st.session_state.questions_asked >= MAX_QUESTIONS:
    st.warning(f"You've reached the demo limit of {MAX_QUESTIONS} questions for this session. Thanks for trying it out!")
    prompt = None

if prompt:
    st.session_state.questions_asked += 1
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        status_box = st.empty()
        cards_box = st.container()
        reasoning_box = st.expander("🧠 Thinking", expanded=False).empty() if show_reasoning else None
        answer_box = st.empty()
        answer_box.markdown(ui.TYPING, unsafe_allow_html=True)

        answer, reasoning, tools_used, results = "", "", [], []
        status = None
        start = time.perf_counter()

        try:
            # Send only the new message; the checkpointer adds the earlier conversation
            query = {"messages": [{"role": "user", "content": prompt}]}
            for chunk, meta in agent.stream(query, config, stream_mode="messages"):
                node = meta.get("langgraph_node")

                if node == "tools":
                    # A finished tool call: show its result as a card
                    results.append((chunk.name, chunk.content))
                    if status is not None:
                        status.write(f"✅ `{chunk.name}` returned data")
                    if show_cards:
                        with cards_box:
                            ui.tool_card(chunk.name, chunk.content)
                    continue

                if node != "model":
                    continue

                for tc in chunk.tool_call_chunks:
                    if tc.get("name"):
                        tools_used.append(tc["name"])
                        if status is None:
                            status = status_box.status("🛠️ Agent is using tools...", expanded=True)
                        icon = ui.TOOLS.get(tc["name"], ("🔧",))[0]
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

        except RateLimitError:
            if status is not None:
                status.update(label="Rate limited", state="error")
            answer = "⏳ The demo is getting a lot of requests right now. Please wait a minute and try again."
            answer_box.warning(answer)

        except Exception as e:
            if status is not None:
                status.update(label="Tool call failed", state="error")
            answer = f"⚠️ Something went wrong: `{e}`"
            answer_box.error(answer)

        elapsed = time.perf_counter() - start
        ui.meta_row(elapsed, len(tools_used))

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "tools": tools_used,
        "results": results,
        "reasoning": reasoning,
        "elapsed": elapsed,
    })
    st.rerun()  # redraw so the starter cards disappear and history renders in order
