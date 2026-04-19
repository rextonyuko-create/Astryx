import streamlit as st
import os
import sqlite3
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
GROQ_MODEL = "llama-3.1-8b-instant"
DB_PATH = "/tmp/chat_history.db"

st.set_page_config(page_title="Astryx", page_icon="✦", layout="wide")

st.markdown("""
<style>
  #MainMenu, footer, header {visibility: hidden;}
  .block-container {padding: 1rem 1.5rem 1rem 1.5rem;}
  section[data-testid="stSidebar"] {background: #0e0e16; border-right: 1px solid rgba(123,110,246,0.2);}
  section[data-testid="stSidebar"] * {color: #e8e6ff !important;}
  .stRadio label {font-size: 13px !important;}
  .stButton > button {
    width: 100%; background: transparent;
    border: 1px solid rgba(123,110,246,0.3);
    color: #9b97c4 !important; border-radius: 8px;
    font-size: 12px; padding: 6px 10px;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background: rgba(123,110,246,0.1);
    border-color: #7B6EF6;
    color: #7B6EF6 !important;
  }
  [data-testid="stChatMessage"] {background: #12121a; border: 1px solid rgba(123,110,246,0.15); border-radius: 10px; margin-bottom: 8px;}
  [data-testid="stChatInput"] input {background: #12121a !important; color: #e8e6ff !important; border: 1px solid rgba(123,110,246,0.3) !important;}
  .main {background: #0a0a0f;}
  .astryx-header {display:flex;align-items:center;gap:12px;padding:12px 0 16px 0;border-bottom:1px solid rgba(123,110,246,0.2);margin-bottom:16px}
  .astryx-logo {width:36px;height:36px;background:#12121a;border:1px solid rgba(123,110,246,0.4);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px}
  .astryx-title {font-family:monospace;font-size:20px;font-weight:700;color:#e8e6ff;letter-spacing:1px}
  .astryx-sub {font-size:10px;color:#7B6EF6;letter-spacing:2px;text-transform:uppercase}
  .online-dot {width:7px;height:7px;background:#2dd4bf;border-radius:50%;display:inline-block;margin-right:5px}
  .section-title {font-size:10px;color:#5a566b;letter-spacing:1.5px;text-transform:uppercase;font-family:monospace;margin:16px 0 8px 0}
</style>
""", unsafe_allow_html=True)

# ── DB ────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT)")
    conn.commit(); conn.close()

def save_message(role, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit(); conn.close()

def load_messages():
    conn = sqlite3.connect(DB_PATH)
    msgs = [{"role": r, "content": c} for r, c in conn.execute("SELECT role, content FROM messages ORDER BY id")]
    conn.close(); return msgs

def clear_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM messages")
    conn.commit(); conn.close()

# ── Groq ──────────────────────────────────────────────────────────────────────
def chat_groq(messages, personality):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY not set. Add it in Streamlit secrets."
    prompts = {
        "Casual": "You are a friendly, warm, casual assistant. Keep it conversational and fun.",
        "Precise": "You are a professional, formal, concise assistant. Be direct and accurate.",
        "Creative": "You are a creative, imaginative assistant. Think outside the box and be expressive."
    }
    client = Groq(api_key=GROQ_API_KEY)
    groq_msgs = [{"role": "system", "content": prompts.get(personality, prompts["Casual"])}]
    groq_msgs += [{"role": m["role"], "content": m["content"]} for m in messages]
    try:
        resp = client.chat.completions.create(model=GROQ_MODEL, messages=groq_msgs, max_tokens=1024)
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# ── Weather ───────────────────────────────────────────────────────────────────
def get_weather(city):
    if not WEATHER_API_KEY:
        return "WEATHER_API_KEY not set."
    try:
        r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric", timeout=5)
        if r.status_code == 200:
            d = r.json()
            return f"{city}: {d['main']['temp']}°C, {d['weather'][0]['description'].capitalize()}"
        return f"Could not fetch weather for {city}."
    except Exception as e:
        return f"Weather error: {e}"

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()
if "personality" not in st.session_state:
    st.session_state.personality = "Casual"
if "prefill" not in st.session_state:
    st.session_state.prefill = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="astryx-header">
      <div class="astryx-logo">✦</div>
      <div>
        <div class="astryx-title">ASTRYX</div>
        <div class="astryx-sub">Neural Interface</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:12px;color:#5a566b;margin-bottom:16px"><span class="online-dot"></span>Online · {GROQ_MODEL}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Mode</div>', unsafe_allow_html=True)
    personality = st.radio("", ["Casual", "Precise", "Creative"], index=["Casual","Precise","Creative"].index(st.session_state.personality), label_visibility="collapsed")
    st.session_state.personality = personality

    st.markdown('<div class="section-title">Quick Actions</div>', unsafe_allow_html=True)

    if st.button("Weather in Bengaluru"):
        st.session_state.prefill = "What is the weather in Bengaluru?"
    if st.button("Surprise me"):
        st.session_state.prefill = "Tell me something surprising and fascinating."
    if st.button("Write Python code"):
        st.session_state.prefill = "Help me write a Python function."
    if st.button("Explain something"):
        st.session_state.prefill = "Explain quantum entanglement in simple terms."

    st.markdown('<div class="section-title">Session</div>', unsafe_allow_html=True)
    st.caption(f"Messages: {len(st.session_state.messages)}")

    if st.button("Clear History"):
        clear_db()
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div style="margin-top:auto;padding-top:24px;font-size:10px;color:#3a3650;font-family:monospace">Powered by Groq · Free tier</div>', unsafe_allow_html=True)

# ── Main chat area ────────────────────────────────────────────────────────────
st.markdown(f'<div style="font-size:11px;color:#5a566b;font-family:monospace;margin-bottom:12px">— session init · {personality.lower()} mode —</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown('<div style="color:#3a3650;font-size:13px;font-family:monospace;text-align:center;padding:40px 0">transmit your first message to begin</div>', unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
prefill_val = st.session_state.prefill
st.session_state.prefill = ""

user_input = st.chat_input("transmit a message…", key="chat_input")

if prefill_val and not user_input:
    user_input = prefill_val

if user_input and user_input.strip():
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message("user", user_input)

    with st.chat_message("assistant"):
        with st.spinner(""):
            reply = chat_groq(st.session_state.messages, st.session_state.personality)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_message("assistant", reply)
    st.rerun()
