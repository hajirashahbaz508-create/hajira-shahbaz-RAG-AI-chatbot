import html
import time

import streamlit as st

st.set_page_config(page_title="Python Notes AI", page_icon="🫧", layout="wide",
                   initial_sidebar_state="expanded")

# ---------- Backend ----------
try:
    import chatbot
    BACKEND_OK, BACKEND_ERR = True, ""
except FileNotFoundError:
    BACKEND_OK, BACKEND_ERR = False, "retrieval_data.pkl not found. Run `python ingest.py` first."
except Exception as e:  # noqa: BLE001
    BACKEND_OK, BACKEND_ERR = False, str(e)

SUGGESTIONS = [
    "What is a list in Python?",
    "Explain for loops",
    "How do functions work?",
    "My name is Alex",
]

# ---------- Themes ----------
THEMES = {
    "Sunset": dict(bg="linear-gradient(135deg,#1a0b2e 0%,#3b1248 45%,#4a1c2a 100%)",
                   a1="#ff7a59", a2="#ffb347", a3="#ff4d8d", inner="#2a1038",
                   text="#fff4ee", muted="rgba(255,244,238,0.65)",
                   glass="rgba(255,255,255,0.08)", strong="rgba(255,255,255,0.15)", border="rgba(255,255,255,0.2)"),
    "Aurora": dict(bg="linear-gradient(135deg,#0b1020 0%,#151038 45%,#0a1a2e 100%)",
                   a1="#7c5cff", a2="#22d3ee", a3="#f472b6", inner="#12163a",
                   text="#eef2ff", muted="rgba(238,242,255,0.62)",
                   glass="rgba(255,255,255,0.08)", strong="rgba(255,255,255,0.14)", border="rgba(255,255,255,0.18)"),
    "Forest": dict(bg="linear-gradient(135deg,#04130f 0%,#0b2a22 50%,#07201f 100%)",
                   a1="#10b981", a2="#a3e635", a3="#2dd4bf", inner="#082019",
                   text="#ecfdf5", muted="rgba(236,253,245,0.62)",
                   glass="rgba(255,255,255,0.07)", strong="rgba(255,255,255,0.14)", border="rgba(255,255,255,0.18)"),
    "Light": dict(bg="linear-gradient(135deg,#eef2ff 0%,#fde7f3 50%,#e0f7fa 100%)",
                  a1="#7c5cff", a2="#06b6d4", a3="#ec4899", inner="#ffffff",
                  text="#1e1b4b", muted="rgba(30,27,75,0.62)",
                  glass="rgba(255,255,255,0.45)", strong="rgba(255,255,255,0.72)", border="rgba(255,255,255,0.85)"),
}
ICONS = {"Sunset": "🌅", "Aurora": "🌌", "Forest": "🌲", "Light": "☀️"}

# Theme lives in the URL (?theme=Forest) so it survives refresh and works on every screen.
theme_name = st.query_params.get("theme", "Sunset")
if theme_name not in THEMES:
    theme_name = "Sunset"
T = THEMES[theme_name]

# ---------- Styling ----------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Sora', sans-serif !important; color: var(--text); }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"]{ display:none !important; }
header[data-testid="stHeader"]{ background: transparent !important; }

/* sidebar open / close buttons stay visible and match the theme */
[data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"]{
  z-index: 1000002 !important; display:flex !important; visibility:visible !important; opacity:1 !important; }
[data-testid="stSidebarCollapsedControl"] button, [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] button{
  background: var(--glass) !important; border:1px solid var(--border) !important; border-radius:14px !important;
  backdrop-filter: blur(16px); color: var(--text) !important; transition: transform .25s, box-shadow .25s; }
[data-testid="stSidebarCollapsedControl"] button:hover, [data-testid="stExpandSidebarButton"]:hover, [data-testid="stSidebarCollapseButton"] button:hover{
  transform: scale(1.1); box-shadow: 0 0 20px var(--a2); }
[data-testid="stSidebarCollapsedControl"] svg, [data-testid="stExpandSidebarButton"] svg, [data-testid="stSidebarCollapseButton"] svg{ color: var(--text) !important; fill: var(--text) !important; }

/* Animated background */
.stApp{ background: var(--bg); background-attachment: fixed; transition: background .6s ease; }
.stApp::before, .stApp::after, .orb{
  content:""; position:fixed; border-radius:50%; filter: blur(80px); opacity:.55; z-index:0; pointer-events:none; }
.stApp::before{ width:520px;height:520px; background:var(--a1); top:-140px; left:-120px; animation: drift1 18s ease-in-out infinite alternate; }
.stApp::after { width:460px;height:460px; background:var(--a2); bottom:-160px; right:-100px; animation: drift2 22s ease-in-out infinite alternate; }
.orb{ width:340px;height:340px; background:var(--a3); top:45%; left:55%; opacity:.28; animation: drift3 26s ease-in-out infinite alternate; }
@keyframes drift1{ to{ transform: translate(220px,160px) scale(1.2);} }
@keyframes drift2{ to{ transform: translate(-240px,-120px) scale(1.15);} }
@keyframes drift3{ to{ transform: translate(-300px,120px) scale(.8);} }

.block-container{ position:relative; z-index:1; max-width: 880px; padding-top: 1.6rem; padding-bottom: 7rem; }

/* Glass header */
.glass{
  background: var(--glass);
  backdrop-filter: blur(22px) saturate(160%); -webkit-backdrop-filter: blur(22px) saturate(160%);
  border: 1px solid var(--border); border-radius: 22px;
  box-shadow: 0 8px 32px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.22);
}
.topbar{ display:flex; align-items:center; gap:16px; padding:16px 22px; margin-bottom: 14px;
  animation: dropIn .8s cubic-bezier(.2,.9,.3,1.2) both; }
@keyframes dropIn{ from{opacity:0; transform: translateY(-28px) scale(.97);} to{opacity:1; transform:none;} }

.logo{ width:46px;height:46px;border-radius:50%; flex:none; position:relative;
  background: conic-gradient(from 0deg, var(--a1), var(--a2), var(--a3), var(--a1));
  animation: spin 7s linear infinite, pulse 3s ease-in-out infinite; box-shadow: 0 0 24px var(--a1); }
.logo::after{ content:""; position:absolute; inset:7px; border-radius:50%; background:var(--inner); }
@keyframes spin{ to{ transform: rotate(360deg);} }
@keyframes pulse{ 50%{ box-shadow: 0 0 40px var(--a2);} }

.title{ font-weight:600; font-size:1.2rem; letter-spacing:.2px; }
.subtitle{ color:var(--muted); font-size:.8rem; margin-top:2px; }
.status{ margin-left:auto; display:flex; align-items:center; gap:8px; font-size:.78rem; color:var(--muted);
  padding:7px 14px; border-radius:999px; background:var(--glass); border:1px solid var(--border); }
.dot{ width:8px;height:8px;border-radius:50%; background:#34d399; box-shadow:0 0 0 0 rgba(52,211,153,.7); animation: ping 1.8s infinite; }
.dot.off{ background:#f87171; animation:none; }
@keyframes ping{ 70%{ box-shadow:0 0 0 9px rgba(52,211,153,0);} 100%{ box-shadow:0 0 0 0 rgba(52,211,153,0);} }

/* Messages */
.row{ display:flex; margin: 12px 0; gap:10px; align-items:flex-end; }
.row.user{ justify-content:flex-end; }
.avatar{ width:34px;height:34px;border-radius:50%; flex:none; display:grid; place-items:center; font-size:.9rem;
  background: linear-gradient(135deg,var(--a1),var(--a2)); box-shadow:0 4px 14px rgba(0,0,0,.3); }
.row.user .avatar{ background: linear-gradient(135deg,var(--a3),var(--a1)); order:2; }
.bubble{ max-width: 76%; padding: 13px 18px; font-size:.93rem; line-height:1.6; border-radius: 20px;
  background: var(--glass); border:1px solid var(--border);
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 6px 24px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.18);
  transition: transform .25s ease, box-shadow .25s ease, background .25s ease; }
.bubble:hover{ transform: translateY(-2px); background: var(--glass-strong); box-shadow: 0 12px 32px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.28); }
.row.bot .bubble{ border-bottom-left-radius: 6px; }
.row.user .bubble{ border-bottom-right-radius: 6px; background: linear-gradient(135deg, var(--a1), var(--a2)); color:#fff; }
.row.user .bubble .time{ color: rgba(255,255,255,.8); }
.row.fresh.bot  .bubble{ animation: popL .5s cubic-bezier(.2,.9,.3,1.3) both; }
.row.fresh.user .bubble{ animation: popR .5s cubic-bezier(.2,.9,.3,1.3) both; }
@keyframes popL{ from{opacity:0; transform: translate(-24px,12px) scale(.9);} to{opacity:1; transform:none;} }
@keyframes popR{ from{opacity:0; transform: translate(24px,12px) scale(.9);} to{opacity:1; transform:none;} }
.time{ display:block; margin-top:6px; font-size:.68rem; color:var(--muted); }

/* Thinking dots + typing cursor */
.typing{ display:inline-flex; gap:6px; padding:4px 2px; }
.typing span{ width:8px;height:8px;border-radius:50%; background:var(--a2); animation: bounce 1.2s infinite ease-in-out; }
.typing span:nth-child(2){ animation-delay:.15s; background:var(--a1);} .typing span:nth-child(3){ animation-delay:.3s; background:var(--a3);}
@keyframes bounce{ 0%,60%,100%{ transform: translateY(0); opacity:.5;} 30%{ transform: translateY(-8px); opacity:1;} }
.cursor{ display:inline-block; width:2px; height:1em; background:var(--a2); margin-left:2px; vertical-align:-2px; animation: blink .8s steps(1) infinite; }
@keyframes blink{ 50%{ opacity:0; } }

/* Welcome */
.hero{ text-align:center; padding: 30px 20px 14px; animation: dropIn .9s .15s both; }
.hero h1{ font-size:2rem; font-weight:600; margin:0 0 8px;
  background: linear-gradient(90deg,var(--text),var(--a1),var(--a2),var(--text)); background-size:200% auto;
  -webkit-background-clip:text; background-clip:text; color:transparent; animation: shine 6s linear infinite; }
@keyframes shine{ to{ background-position: 200% center; } }
.hero p{ color:var(--muted); font-size:.92rem; margin-bottom: 4px; }

/* Buttons (theme pills, chips, clear) */
.stButton > button{
  width:100%; color:var(--text); font-family:'Sora',sans-serif; font-size:.82rem;
  background: var(--glass); border:1px solid var(--border); border-radius:999px; padding:8px 14px;
  backdrop-filter: blur(14px); transition: all .25s ease; box-shadow: inset 0 1px 0 rgba(255,255,255,.15); }
.stButton > button:hover{ transform: translateY(-3px) scale(1.03); border-color: var(--a2);
  background: var(--glass-strong); box-shadow: 0 10px 26px rgba(0,0,0,.25); color:var(--text); }
.stButton > button:active{ transform: scale(.97); }
.stButton > button p{ color: inherit; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"]{
  background: linear-gradient(135deg,var(--a1),var(--a2)); border-color: transparent; color:#fff; font-weight:600;
  box-shadow: 0 6px 22px rgba(0,0,0,.3); }

/* Chat input */
[data-testid="stBottom"], [data-testid="stBottom"] > div{ background: transparent !important; }
[data-testid="stChatInput"]{
  background: var(--glass) !important; border:1px solid var(--border) !important; border-radius:22px !important;
  backdrop-filter: blur(24px); box-shadow: 0 10px 40px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.2);
  transition: box-shadow .3s ease, border-color .3s ease, transform .3s ease; }
[data-testid="stChatInput"]:focus-within{ border-color: var(--a2) !important; transform: translateY(-2px);
  box-shadow: 0 0 0 3px rgba(255,255,255,.1), 0 14px 44px rgba(0,0,0,.35); }
[data-testid="stChatInput"] textarea{ color: var(--text) !important; font-family:'Sora',sans-serif !important; }
[data-testid="stChatInput"] textarea::placeholder{ color: var(--muted) !important; }
[data-testid="stChatInput"] button{ background: linear-gradient(135deg,var(--a1),var(--a2)) !important; border-radius:14px !important; transition: transform .2s; }
[data-testid="stChatInput"] button:hover{ transform: scale(1.12) rotate(-8deg); }

/* Sidebar */
section[data-testid="stSidebar"]{ background: var(--glass) !important; backdrop-filter: blur(26px); border-right:1px solid var(--border); }
section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] h4{ color: var(--text); }
.side-card{ padding:16px 18px; margin-bottom:14px; border-radius:18px; background:var(--glass); border:1px solid var(--border); transition: transform .25s; }
.side-card:hover{ transform: translateX(4px); }
.side-card h4{ margin:0 0 6px; font-size:.82rem; font-weight:600; }
.side-card p{ margin:0; font-size:.78rem; color:var(--muted); line-height:1.5; }
.stat{ font-size:1.6rem; font-weight:600; background:linear-gradient(90deg,var(--a1),var(--a3)); -webkit-background-clip:text; background-clip:text; color:transparent; }

::-webkit-scrollbar{ width:8px; } ::-webkit-scrollbar-thumb{ background: rgba(255,255,255,.25); border-radius:8px; }
@media (max-width:640px){ .bubble{ max-width:88%; } .hero h1{ font-size:1.5rem; } }
@media (prefers-reduced-motion: reduce){ *{ animation: none !important; transition: none !important; } }
</style>
<div class="orb"></div>
"""
THEME_VARS = f"""<style>:root{{
  --bg:{T['bg']}; --a1:{T['a1']}; --a2:{T['a2']}; --a3:{T['a3']}; --inner:{T['inner']};
  --text:{T['text']}; --muted:{T['muted']}; --glass:{T['glass']}; --glass-strong:{T['strong']}; --border:{T['border']};
}}</style>"""
st.markdown(THEME_VARS + CSS, unsafe_allow_html=True)

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None


def clear_chat():
    st.session_state.messages = []
    if BACKEND_OK:
        chatbot.reset_memory()


def fmt(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")


def bubble(role: str, text: str, ts: str = "", fresh: bool = False, cursor: bool = False) -> str:
    icon = "🧑" if role == "user" else "✨"
    cls = f"row {role}" + (" fresh" if fresh else "")
    cur = '<span class="cursor"></span>' if cursor else ""
    return (f'<div class="{cls}"><div class="avatar">{icon}</div>'
            f'<div class="bubble">{fmt(text)}{cur}<span class="time">{ts}</span></div></div>')


THINKING = ('<div class="row bot fresh"><div class="avatar">✨</div><div class="bubble">'
            '<div class="typing"><span></span><span></span><span></span></div></div></div>')

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🫧 Control panel")
    n_user = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown(f'<div class="side-card"><h4>Questions asked</h4><div class="stat">{n_user}</div></div>',
                unsafe_allow_html=True)
    remembered = chatbot.memory.get("name") if BACKEND_OK else None
    shown_name = html.escape(remembered) if remembered else "Nothing yet. Say “My name is …”"
    st.markdown(f'<div class="side-card"><h4>Remembered name</h4><p>{shown_name}</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-card"><h4>How it works</h4><p>Your question is embedded, matched against chunks of '
                'your PDF notes, and answered by a local Llama model. Everything runs offline.</p></div>',
                unsafe_allow_html=True)
    st.button("🗑️  Clear conversation", key="clear_side", on_click=clear_chat)

# ---------- Header ----------
dot = "dot" if BACKEND_OK else "dot off"
label = "Offline · ready" if BACKEND_OK else "Backend error"
st.markdown(
    f'''<div class="glass topbar"><div class="logo"></div>
    <div><div class="title">Python Notes AI</div><div class="subtitle">Ask anything from your PDF notes</div></div>
    <div class="status"><span class="{dot}"></span>{label}</div></div>''',
    unsafe_allow_html=True)

# ---------- Theme switcher (main page, so it is always reachable) ----------
tcols = st.columns(len(THEMES) + 1)
for col, name in zip(tcols, THEMES):
    if col.button(f"{ICONS[name]} {name}", key=f"theme_{name}",
                  type="primary" if name == theme_name else "secondary"):
        st.query_params["theme"] = name
        st.rerun()
tcols[-1].button("🗑️ Clear", key="clear_main", on_click=clear_chat)

if not BACKEND_OK:
    st.error(BACKEND_ERR)
    st.stop()

# ---------- Welcome + chips ----------
if not st.session_state.messages:
    st.markdown('<div class="hero"><h1>What do you want to learn today?</h1>'
                '<p>Pick a starter or type your own question below.</p></div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, s in enumerate(SUGGESTIONS):
        if cols[i % 2].button(s, key=f"chip{i}"):
            st.session_state.pending = s
            st.rerun()

# ---------- History ----------
for m in st.session_state.messages:
    st.markdown(bubble(m["role"], m["content"], m["ts"], fresh=m.get("fresh", False)), unsafe_allow_html=True)
    m["fresh"] = False

# ---------- New input ----------
typed = st.chat_input("Ask about your Python notes…")
question = typed or st.session_state.pending
st.session_state.pending = None

if question:
    ts = time.strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": question, "ts": ts, "fresh": False})
    st.markdown(bubble("user", question, ts, fresh=True), unsafe_allow_html=True)

    slot = st.empty()
    slot.markdown(THINKING, unsafe_allow_html=True)
    try:
        reply = chatbot.ask_chatbot(question)
    except Exception as e:  # noqa: BLE001
        reply = f"Something went wrong: {e}. Check that Ollama is running."

    # typewriter effect
    shown = []
    for w in reply.split(" "):
        shown.append(w)
        slot.markdown(bubble("bot", " ".join(shown), "", fresh=(len(shown) == 1), cursor=True),
                      unsafe_allow_html=True)
        time.sleep(0.03)
    ts2 = time.strftime("%H:%M")
    slot.markdown(bubble("bot", reply, ts2), unsafe_allow_html=True)
    st.session_state.messages.append({"role": "bot", "content": reply, "ts": ts2, "fresh": False})
    st.rerun()
