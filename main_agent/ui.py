import json
from html import escape
from urllib.parse import urlparse
import streamlit as st


TOOLS = {
    "tavily_search":      ("🔍", "Web search", "News and up-to-date information"),
    "get_weather":        ("🌤️", "Weather", "Current weather for any city"),
    "world_clock":        ("🕒", "World clock", "Local time in any timezone"),
    "currency_converter": ("💱", "Currency", "Latest exchange rates"),
}

EXAMPLES = [
    ("🌤️", "Weather", "What's the weather in Mumbai?"),
    ("🕒", "World clock", "What time is it in New York and Tokyo?"),
    ("💱", "Currency", "Convert 100 USD to INR"),
    ("🔍", "Web search", "Latest AI news headlines"),
]

WEATHER_STYLE = {
    "Clear":        ("☀️", "🌙", "linear-gradient(135deg,#F59E0B 0%,#F97316 100%)"),
    "Clouds":       ("☁️", "☁️", "linear-gradient(135deg,#64748B 0%,#94A3B8 100%)"),
    "Rain":         ("🌧️", "🌧️", "linear-gradient(135deg,#2563EB 0%,#0EA5E9 100%)"),
    "Drizzle":      ("🌦️", "🌦️", "linear-gradient(135deg,#0EA5E9 0%,#38BDF8 100%)"),
    "Thunderstorm": ("⛈️", "⛈️", "linear-gradient(135deg,#312E81 0%,#6D28D9 100%)"),
    "Snow":         ("❄️", "❄️", "linear-gradient(135deg,#60A5FA 0%,#A5B4FC 100%)"),
}
WEATHER_NIGHT_BG = "linear-gradient(135deg,#1E1B4B 0%,#4338CA 100%)"
WEATHER_MIST = ("🌫️", "🌫️", "linear-gradient(135deg,#6B7280 0%,#9CA3AF 100%)")

CURRENCY_FLAGS = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "INR": "🇮🇳", "GBP": "🇬🇧", "JPY": "🇯🇵", "CNY": "🇨🇳",
    "AUD": "🇦🇺", "CAD": "🇨🇦", "CHF": "🇨🇭", "SGD": "🇸🇬", "HKD": "🇭🇰", "KRW": "🇰🇷",
    "BRL": "🇧🇷", "MXN": "🇲🇽", "ZAR": "🇿🇦", "SEK": "🇸🇪", "NZD": "🇳🇿", "TRY": "🇹🇷",
}


## Page styles
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stButton button, [data-testid="stChatInput"] textarea {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(99,102,241,0.10), transparent 32%),
        radial-gradient(circle at 88% 4%, rgba(236,72,153,0.08), transparent 30%),
        #FAFAFF;
}
[data-testid="stHeader"], .stAppHeader { background: transparent !important; }
.block-container { padding-top: 3.5rem; max-width: 820px; }

/* Hero */
.hero {
    position: relative; overflow: hidden;
    padding: 1.8rem 1.8rem 1.5rem;
    border-radius: 22px;
    background: linear-gradient(120deg, #4F46E5, #7C3AED, #DB2777, #4F46E5);
    background-size: 300% 300%;
    animation: gradientShift 12s ease infinite;
    color: white;
    box-shadow: 0 18px 40px -18px rgba(79,70,229,0.55);
    margin-bottom: 1.4rem;
}
.hero::after {
    content: ""; position: absolute; right: -60px; top: -60px;
    width: 220px; height: 220px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.28), transparent 70%);
}
.hero-top { display: flex; align-items: center; gap: 0.9rem; }
.hero-orb {
    font-size: 2.1rem; width: 58px; height: 58px; flex: none;
    display: flex; align-items: center; justify-content: center;
    border-radius: 16px; background: rgba(255,255,255,0.18);
    backdrop-filter: blur(6px); animation: float 4s ease-in-out infinite;
}
.hero h1 { color: white !important; font-size: 1.85rem; font-weight: 800; margin: 0; padding: 0; letter-spacing: -0.02em; }
.hero p { color: rgba(255,255,255,0.88); margin: 0.15rem 0 0; font-size: 0.97rem; }
.hero-badges { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 1.1rem; position: relative; z-index: 1; }
.badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.28rem 0.7rem; border-radius: 999px;
    background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.25);
    font-size: 0.78rem; font-weight: 600; color: white;
}
.live-dot { width: 8px; height: 8px; border-radius: 50%; background: #4ADE80; animation: pulse 1.6s infinite; }

/* Empty state */
.welcome { text-align: center; margin: 0.4rem 0 1rem; }
.welcome h3 { font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.1rem; }
.welcome p { color: #6B7280; margin: 0; }
.st-key-examples [data-testid="stButton"], .st-key-examples .stButton { width: 100%; }
.st-key-examples button {
    min-height: 96px; width: 100% !important;
    justify-content: flex-start; text-align: left;
    padding: 0.9rem 1rem; border-radius: 16px;
    border: 1px solid #E5E7EB; background: white;
    box-shadow: 0 2px 10px -4px rgba(17,24,39,0.08);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.st-key-examples button:hover {
    transform: translateY(-3px); border-color: #A5B4FC;
    box-shadow: 0 12px 24px -12px rgba(79,70,229,0.45);
}
.st-key-examples button > div, .st-key-examples button [data-testid="stMarkdownContainer"] {
    width: 100%; justify-content: flex-start; text-align: left;
}
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: transparent; }
.st-key-examples button p { font-size: 0.92rem; line-height: 1.45; color: #374151; }
.st-key-examples button strong { display: block; margin-bottom: 0.25rem; color: #4F46E5; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; }

/* Chat */
[data-testid="stChatMessage"] {
    border-radius: 18px; padding: 0.9rem 1rem; margin-bottom: 0.6rem;
    background: white; border: 1px solid #EEF0F6;
    box-shadow: 0 6px 18px -12px rgba(17,24,39,0.18);
    animation: fadeUp .35s ease;
}
[data-testid="stChatInput"] {
    border-radius: 18px !important;
    box-shadow: 0 10px 30px -14px rgba(79,70,229,0.45);
}

.tool-pill {
    display: inline-flex; align-items: center; gap: 0.25rem;
    padding: 0.18rem 0.65rem; margin: 0 0.35rem 0.5rem 0;
    border-radius: 999px; background: #EEF2FF; color: #4F46E5;
    font-size: 0.76rem; font-weight: 700;
}
.meta-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; }
.meta-chip {
    font-size: 0.72rem; font-weight: 600; color: #6B7280;
    padding: 0.15rem 0.55rem; border-radius: 999px; background: #F3F4F6;
}

/* Typing indicator */
.typing { display: inline-flex; gap: 5px; padding: 0.4rem 0; }
.typing span { width: 8px; height: 8px; border-radius: 50%; background: #A5B4FC; animation: blink 1.2s infinite; }
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }

/* Result cards */
.card { border-radius: 18px; margin: 0.2rem 0 0.8rem; animation: fadeUp .4s ease; overflow: hidden; }
.card-label { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.85; }

.weather-card { color: white; padding: 1.1rem 1.25rem; }
.weather-main { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.weather-city { font-size: 1.15rem; font-weight: 800; }
.weather-desc { font-size: 0.9rem; opacity: 0.92; text-transform: capitalize; }
.weather-temp { font-size: 2.6rem; font-weight: 800; line-height: 1; letter-spacing: -0.03em; }
.weather-icon { font-size: 3rem; line-height: 1; animation: float 4s ease-in-out infinite; }
.weather-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-top: 0.9rem; }
.weather-stat { background: rgba(255,255,255,0.18); border-radius: 12px; padding: 0.45rem 0.55rem; }
.weather-stat b { display: block; font-size: 0.95rem; }
.weather-stat span { font-size: 0.68rem; opacity: 0.9; }

.fx-card { background: white; border: 1px solid #E0E7FF; padding: 1.1rem 1.25rem; }
.fx-card .card-label { color: #6366F1; }
.fx-row { display: flex; align-items: center; justify-content: space-between; gap: 0.6rem; margin-top: 0.5rem; }
.fx-side { flex: 1; background: #F5F7FF; border-radius: 14px; padding: 0.7rem 0.85rem; }
.fx-side .code { font-size: 0.78rem; font-weight: 700; color: #6B7280; }
.fx-side .val { font-size: 1.45rem; font-weight: 800; color: #111827; letter-spacing: -0.02em; word-break: break-all; }
.fx-arrow {
    flex: none; width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg,#6366F1,#EC4899); color: white; font-weight: 800;
}
.fx-foot { margin-top: 0.6rem; font-size: 0.78rem; color: #6B7280; }

.clock-card {
    background: linear-gradient(135deg,#0F172A,#1E293B); color: white;
    padding: 1.1rem 1.25rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.clock-time { font-family: 'JetBrains Mono', monospace; font-size: 2.3rem; font-weight: 700; color: #A5F3FC; letter-spacing: 0.02em; }
.clock-zone { font-size: 1rem; font-weight: 700; }
.clock-date { font-size: 0.82rem; color: #CBD5E1; }
.clock-emoji { font-size: 2.6rem; }

.news-card { background: white; border: 1px solid #EEF0F6; padding: 1rem 1.1rem; }
.news-card .card-label { color: #6366F1; margin-bottom: 0.4rem; }
.news-item {
    display: flex; gap: 0.7rem; padding: 0.65rem 0.5rem; border-radius: 12px;
    text-decoration: none !important; transition: background .15s ease;
}
.news-item:hover { background: #F5F7FF; }
.news-item img { width: 22px; height: 22px; border-radius: 6px; margin-top: 2px; flex: none; }
.news-title { font-weight: 700; color: #111827; font-size: 0.92rem; line-height: 1.35; }
.news-domain { font-size: 0.72rem; color: #6366F1; font-weight: 600; }
.news-snippet { font-size: 0.8rem; color: #6B7280; line-height: 1.4; margin-top: 0.15rem; }

/* Sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #FFFFFF 0%, #F5F6FB 100%); border-right: 1px solid #EEF0F6; }
.side-brand { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem; }
.side-brand .logo {
    width: 40px; height: 40px; border-radius: 12px; font-size: 1.3rem;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg,#6366F1,#EC4899);
}
.side-brand b { display: block; font-size: 1.02rem; }
.side-brand span { font-size: 0.75rem; color: #6B7280; }
.side-title { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #9CA3AF; margin: 0.8rem 0 0.4rem; }
.tool-row {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.5rem 0.6rem; border-radius: 12px; margin-bottom: 0.3rem;
    background: white; border: 1px solid #EEF0F6;
}
.tool-row .ico { font-size: 1.1rem; }
.tool-row b { display: block; font-size: 0.84rem; }
.tool-row small { font-size: 0.72rem; color: #6B7280; }
.tool-row .on { margin-left: auto; width: 8px; height: 8px; border-radius: 50%; background: #22C55E; box-shadow: 0 0 0 3px rgba(34,197,94,0.18); }
.side-foot { font-size: 0.72rem; color: #9CA3AF; margin-top: 1rem; }

@keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(74,222,128,0.7); } 70% { box-shadow: 0 0 0 7px rgba(74,222,128,0); } 100% { box-shadow: 0 0 0 0 rgba(74,222,128,0); } }
@keyframes blink { 0%, 80%, 100% { opacity: 0.3; transform: scale(0.85); } 40% { opacity: 1; transform: scale(1); } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}
@media (max-width: 640px) {
    .weather-stats { grid-template-columns: repeat(2, 1fr); }
    .clock-time { font-size: 1.8rem; }
    .fx-row { flex-direction: column; align-items: stretch; }
    .fx-arrow { align-self: center; transform: rotate(90deg); }
}
</style>
"""

TYPING = '<div class="typing"><span></span><span></span><span></span></div>'


def html(markup):
    # Collapse whitespace so markdown never turns indented HTML into a code block
    st.markdown(" ".join(markup.split()), unsafe_allow_html=True)


## Layout pieces
def hero(model_name, max_messages):
    html(f"""
    <div class="hero">
      <div class="hero-top">
        <div class="hero-orb">🤖</div>
        <div>
          <h1>AI Agent</h1>
          <p>Searches the web, checks the weather, tells the time anywhere and converts currencies.</p>
        </div>
      </div>
      <div class="hero-badges">
        <span class="badge"><span class="live-dot"></span>Live streaming</span>
        <span class="badge">⚡ {escape(model_name)} on Groq</span>
        <span class="badge">🛠️ {len(TOOLS)} tools</span>
        <span class="badge">🧠 Memory · last {max_messages} msgs</span>
        <span class="badge">🦜 LangGraph</span>
      </div>
    </div>""")


def sidebar_brand():
    html("""
    <div class="side-brand">
      <div class="logo">🤖</div>
      <div><b>AI Agent</b><span>Tool-calling assistant</span></div>
    </div>
    <div class="side-title">Tools</div>""")
    html("".join(
        f'<div class="tool-row"><span class="ico">{icon}</span>'
        f'<div><b>{name}</b><small>{desc}</small></div><span class="on"></span></div>'
        for icon, name, desc in TOOLS.values()
    ))


def welcome():
    html("""
    <div class="welcome">
      <h3>What can I help you with? ✨</h3>
      <p>Pick a starter below or type your own question.</p>
    </div>""")


def example_cards():
    """Show starter cards; return the prompt of the one clicked."""
    clicked = None
    with st.container(key="examples"):
        cols = st.columns(2)
        for i, (icon, label, text) in enumerate(EXAMPLES):
            if cols[i % 2].button(f"{icon} **{label}**\n\n{text}", key=f"ex_{i}", width="stretch"):
                clicked = text
    return clicked


def tool_pills(tools):
    html("".join(
        f'<span class="tool-pill">{TOOLS.get(t, ("🔧",))[0]} {escape(t)}</span>' for t in dict.fromkeys(tools)
    ))


def meta_row(elapsed, n_tools):
    chips = [f"⏱ {elapsed:.1f}s"]
    if n_tools:
        chips.append(f"🛠️ {n_tools} tool call{'s' if n_tools > 1 else ''}")
    html('<div class="meta-row">' + "".join(f'<span class="meta-chip">{c}</span>' for c in chips) + "</div>")


## Tool result cards
def _num(value, digits=2):
    try:
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return escape(str(value))


def weather_card(d):
    day_icon, night_icon, bg = WEATHER_STYLE.get(d.get("weather"), WEATHER_MIST)
    is_day = d.get("is_day", True)
    icon = day_icon if is_day else night_icon
    if not is_day and d.get("weather") == "Clear":
        bg = WEATHER_NIGHT_BG
    place = escape(f"{d.get('city', '')}{', ' + d['country'] if d.get('country') else ''}")
    stats = [
        (f"{_num(d.get('feels_like'), 0)}°", "Feels like"),
        (f"{d.get('humidity', '–')}%", "Humidity"),
        (f"{_num(d.get('wind_speed_m_per_s'), 1)} m/s", "Wind"),
        (f"{d.get('pressure', '–')}", "hPa"),
    ]
    html(f"""
    <div class="card weather-card" style="background:{bg}">
      <div class="card-label">Weather now</div>
      <div class="weather-main">
        <div>
          <div class="weather-city">📍 {place}</div>
          <div class="weather-desc">{escape(str(d.get('description', d.get('weather', ''))))}</div>
          <div class="weather-temp">{_num(d.get('temp'), 0)}°C</div>
        </div>
        <div class="weather-icon">{icon}</div>
      </div>
      <div class="weather-stats">
        {"".join(f'<div class="weather-stat"><b>{v}</b><span>{k}</span></div>' for v, k in stats)}
      </div>
    </div>""")


def currency_card(d):
    src, dst = escape(str(d.get("from", ""))), escape(str(d.get("to", "")))
    rate = d.get("rate")
    rate_line = f"1 {src} = {_num(rate, 4)} {dst} · " if rate else ""
    html(f"""
    <div class="card fx-card">
      <div class="card-label">💱 Currency conversion</div>
      <div class="fx-row">
        <div class="fx-side"><div class="code">{CURRENCY_FLAGS.get(src, '💰')} {src}</div><div class="val">{_num(d.get('amount'))}</div></div>
        <div class="fx-arrow">→</div>
        <div class="fx-side"><div class="code">{CURRENCY_FLAGS.get(dst, '💰')} {dst}</div><div class="val">{_num(d.get('converted_amount'))}</div></div>
      </div>
      <div class="fx-foot">{rate_line}ECB reference rate on {escape(str(d.get('rate_date', '')))}</div>
    </div>""")


def clock_card(d):
    time_str = str(d.get("time", ""))
    try:
        hour = int(time_str.split(":")[0])
    except ValueError:
        hour = 12
    emoji = "🌅" if 5 <= hour < 8 else "☀️" if 8 <= hour < 17 else "🌇" if 17 <= hour < 20 else "🌙"
    zone = escape(str(d.get("timezone", "")).replace("_", " "))
    html(f"""
    <div class="card clock-card">
      <div>
        <div class="card-label">🕒 Local time</div>
        <div class="clock-time">{escape(time_str)}</div>
        <div class="clock-zone">{zone}</div>
        <div class="clock-date">{escape(str(d.get('date', '')))} · {escape(str(d.get('abbreviation', '')))} (UTC{escape(str(d.get('utc_offset', '')))})</div>
      </div>
      <div class="clock-emoji">{emoji}</div>
    </div>""")


def news_card(d):
    items = []
    for r in d.get("results", [])[:3]:
        url = str(r.get("url", ""))
        if not url.startswith(("http://", "https://")):
            continue
        domain = urlparse(url).netloc.removeprefix("www.")
        snippet = str(r.get("content", ""))
        snippet = snippet[:160] + "…" if len(snippet) > 160 else snippet
        items.append(f"""
        <a class="news-item" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">
          <img src="https://www.google.com/s2/favicons?domain={escape(domain, quote=True)}&sz=64" alt="">
          <div>
            <div class="news-domain">{escape(domain)}</div>
            <div class="news-title">{escape(str(r.get('title', domain)))}</div>
            <div class="news-snippet">{escape(snippet)}</div>
          </div>
        </a>""")
    if items:
        html(f'<div class="card news-card"><div class="card-label">🔍 Top sources</div>{"".join(items)}</div>')


CARDS = {
    "get_weather": weather_card,
    "currency_converter": currency_card,
    "world_clock": clock_card,
    "tavily_search": news_card,
}


def tool_card(name, content):
    """Render a tool result as a visual card; errors and unknown tools are skipped."""
    render = CARDS.get(name)
    if render is None:
        return
    try:
        data = json.loads(content) if isinstance(content, str) else content
    except json.JSONDecodeError:
        return  # tool returned an error message, the model will explain it
    if isinstance(data, dict):
        render(data)
