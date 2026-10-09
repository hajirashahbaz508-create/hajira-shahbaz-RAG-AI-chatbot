import html
import time

import streamlit as st

st.set_page_config(page_title="Python Notes AI", page_icon="🫧", layout="wide")

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

# ---------- Styling ----------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');

:root{
  --glass: rgba(255,255,255,0.08);
  --glass-strong: rgba(255,255,255,0.14);
  --border: rgba(255,255,255,0.18);
  --text: #eef2ff;
  --muted: rgba(238,242,255,0.62);
  --a1: #7c5cff;
  --a2: #22d3ee;
  --a3: #f472b6;
}

html, body, [class*="css"], .stApp { font-family: 'Sora', sans-serif !important; color: var(--text); }
#MainMenu, footer, header[data-testid="stHeader"] { display:none !important; }

/* Animated aurora background */
.stApp{
  background: linear-gradient(135deg,#0b1020 0%,#151038 45%,#0a1a2e 100%);
  background-attachment: fixed;
}
.stApp::before, .stApp::after, .orb{
  content:""; position:fixed; border-radius:50%; filter: blur(80px); opacity:.55;
  z-index:0; pointer-events:none;
}
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
  backdrop-filter: blur(22px) saturate(160%);
  -webkit-backdrop-filter: blur(22px) saturate(160%);
  border: 1px solid var(--border);
  border-radius: 22px;
  box-shadow: 0 8px 32px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.22);
}
.topbar{ display:flex; align-items:center; gap:16px; padding:16px 22px; margin-bottom: 18px;
  animation: dropIn .8s cubic-bezier(.2,.9,.3,1.2) both; }
@keyframes dropIn{ from{opacity:0; transform: translateY(-28px) scale(.97);} to{opacity:1; transform:none;} }

.logo{ width:46px;height:46px;border-radius:50%; flex:none;
  background: conic-gradient(from 0deg, var(--a1), var(--a2), var(--a3), var(--a1));
  animation: spin 7s linear infinite, pulse 3s ease-in-out infinite;
  box-shadow: 0 0 24px rgba(124,92,255,.7); position:relative; }
.logo::after{ content:""; position:absolute; inset:7px; border-radius:50%; background:#12163a; }
@keyframes spin{ to{ transform: rotate(360deg);} }
@keyframes pulse{ 50%{ box-shadow: 0 0 40px rgba(34,211,238,.85);} }

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
  background: linear-gradient(135deg,var(--a1),var(--a2)); box-shadow:0 4px 14px rgba(0,0,0,.35); }
.row.user .avatar{ background: linear-gradient(135deg,var(--a3),var(--a1)); order:2; }
.bubble{ max-width: 76%; padding: 13px 18px; font-size:.93rem; line-height:1.6; border-radius: 20px;
  background: var(--glass); border:1px solid var(--border);
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 6px 24px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.18);
  transition: transform .25s ease, box-shadow .25s ease, background .25s ease; }
.bubble:hover{ transform: translateY(-2px); background: var(--glass-strong); box-shadow: 0 12px 32px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.28); }
.row.bot .bubble{ border-bottom-left-radius: 6px; }
.row.user .bubble{ border-bottom-right-radius: 6px;
  background: linear-gradient(135deg, rgba(124,92,255,.55), rgba(34,211,238,.35)); }
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
.hero{ text-align:center; padding: 38px 20px 18px; animation: dropIn .9s .15s both; }
.hero h1{ font-size:2rem; font-weight:600; margin:0 0 8px;
  background: linear-gradient(90deg,#fff,#a5b4fc,#67e8f9,#fff); background-size:200% auto;
  -webkit-background-clip:text; background-clip:text; color:transparent; animation: shine 6s linear infinite; }
@keyframes shine{ to{ background-position: 200% center; } }
.hero p{ color:var(--muted); font-size:.92rem; margin-bottom: 4px; }

/* Buttons (suggestion chips, sidebar) */
.stButton > button{
  width:100%; color:var(--text); font-family:'Sora',sans-serif; font-size:.82rem;
  background: var(--glass); border:1px solid var(--border); border-radius:999px; padding:10px 14px;
  backdrop-filter: blur(14px); transition: all .25s ease; box-shadow: inset 0 1px 0 rgba(255,255,255,.15);
}
.stButton > button:hover{ transform: translateY(-3px) scale(1.03); border-color: var(--a2);
  background: var(--glass-strong); box-shadow: 0 10px 26px rgba(34,211,238,.25); color:#fff; }
.stButton > button:active{ transform: scale(.97); }

/* Chat input */
[data-testid="stBottom"], [data-testid="stBottom"] > div{ background: transparent !important; }
[data-testid="stChatInput"]{
  background: var(--glass) !important; border:1px solid var(--border) !important; border-radius:22px !important;
  backdrop-filter: blur(24px); box-shadow: 0 10px 40px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.2);
  transition: box-shadow .3s ease, border-color .3s ease, transform .3s ease;
}
[data-testid="stChatInput"]:focus-within{ border-color: var(--a2) !important; transform: translateY(-2px);
  box-shadow: 0 0 0 3px rgba(34,211,238,.18), 0 14px 44px rgba(124,92,255,.35); }
[data-testid="stChatInput"] textarea{ color: var(--text) !important; font-family:'Sora',sans-serif !important; }
[data-testid="stChatInput"] textarea::placeholder{ color: var(--muted) !important; }
[data-testid="stChatInput"] button{ background: linear-gradient(135deg,var(--a1),var(--a2)) !important; border-radius:14px !important; transition: transform .2s; }
[data-testid="stChatInput"] button:hover{ transform: scale(1.12) rotate(-8deg); }

/* Sidebar */
section[data-testid="stSidebar"]{ background: rgba(255,255,255,.04) !important; backdrop-filter: blur(26px);
  border-right:1px solid var(--border); }
section[data-testid="stSidebar"] *{ color: var(--text); }
.side-card{ padding:16px 18px; margin-bottom:14px; border-radius:18px; background:var(--glass); border:1px solid var(--border);
  transition: transform .25s; }
.side-card:hover{ transform: translateX(4px); }
.side-card h4{ margin:0 0 6px; font-size:.82rem; font-weight:600; }
.side-card p{ margin:0; font-size:.78rem; color:var(--muted); line-height:1.5; }
.stat{ font-size:1.6rem; font-weight:600; background:linear-gradient(90deg,var(--a2),var(--a3)); -webkit-background-clip:text; color:transparent; }

::-webkit-scrollbar{ width:8px; } ::-webkit-scrollbar-thumb{ background: rgba(255,255,255,.2); border-radius:8px; }
@media (max-width:640px){ .bubble{ max-width:88%; } .hero h1{ font-size:1.5rem; } }
@media (prefers-reduced-motion: reduce){ *{ animation: none !important; transition: none !important; } }
</style>
<div class="orb"></div>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None


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
    st.markdown(
        f'<div class="side-card"><h4>Remembered name</h4><p>{html.escape(remembered) if remembered else "Nothing yet. Say “My name is …”"}</p></div>',
        unsafe_allow_html=True)
    st.markdown('<div class="side-card"><h4>How it works</h4><p>Your question is embedded, matched against chunks of '
                'your PDF notes, and answered by a local Llama model. Everything runs offline.</p></div>',
                unsafe_allow_html=True)
    if st.button("🗑️  Clear conversation"):
        st.session_state.messages = []
        if BACKEND_OK:
            chatbot.reset_memory()
        st.rerun()

# ---------- Header ----------
dot = "dot" if BACKEND_OK else "dot off"
label = "Offline · ready" if BACKEND_OK else "Backend error"
st.markdown(
    f'''<div class="glass topbar"><div class="logo"></div>
    <div><div class="title">Python Notes AI</div><div class="subtitle">Ask anything from your PDF notes</div></div>
    <div class="status"><span class="{dot}"></span>{label}</div></div>''',
    unsafe_allow_html=True)

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
    st.session_state.messages.append({"role": "user", "content": question, "ts": ts, "fresh": True})
    st.markdown(bubble("user", question, ts, fresh=True), unsafe_allow_html=True)
    st.session_state.messages[-1]["fresh"] = False

    slot = st.empty()
    slot.markdown(THINKING, unsafe_allow_html=True)
    try:
        reply = chatbot.ask_chatbot(question)
    except Exception as e:  # noqa: BLE001
        reply = f"Something went wrong: {e}. Check that Ollama is running."

    # typewriter effect
    words, shown = reply.split(" "), []
    for w in words:
        shown.append(w)
        slot.markdown(bubble("bot", " ".join(shown), "", fresh=(len(shown) == 1), cursor=True),
                      unsafe_allow_html=True)
        time.sleep(0.03)
    ts2 = time.strftime("%H:%M")
    slot.markdown(bubble("bot", reply, ts2), unsafe_allow_html=True)
    st.session_state.messages.append({"role": "bot", "content": reply, "ts": ts2, "fresh": False})
    st.rerun()
