import os
import threading
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Lightweight API server imports
from flask import Flask, request, jsonify
from flask_cors import CORS

st.set_page_config(page_title='Astryx — Stellar Intelligence', layout='wide')

# Load environment and Groq config
load_dotenv('.env', override=True)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')

try:
    import groq
    groq_available = True
except Exception:
    groq_available = False

client = None
if groq_available and GROQ_API_KEY:
    try:
        client = groq.Groq(api_key=GROQ_API_KEY)
    except Exception:
        client = None


def start_api_server(host='127.0.0.1', port=8503):
    app = Flask('astryx_api')
    CORS(app)

    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.get_json(force=True)
        user_msg = (data or {}).get('message', '')
        if not user_msg:
            return jsonify({'error': 'No message provided'}), 400

        # If Groq client is available, call the model; else return an informative error
        if client is None:
            return jsonify({'error': 'LLM client not configured or unavailable.'}), 500

        try:
            resp = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": user_msg}]
            )
            bot_text = resp.choices[0].message.content
            return jsonify({'reply': bot_text})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Run in a thread
    thread = threading.Thread(target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False), daemon=True)
    thread.start()
    return thread


# Start API server once per Streamlit session
if 'api_thread' not in st.session_state:
    st.session_state.api_thread = None
    try:
        st.session_state.api_thread = start_api_server()
    except Exception as e:
        st.warning(f'Could not start local API server: {e}')

# Render the static UI (ui.html) via components
ui_path = Path(__file__).with_name('ui.html')
if ui_path.exists():
    html = ui_path.read_text(encoding='utf-8')
    components.html(html, height=940, scrolling=True)
else:
    st.error('Cannot find ui.html. Please add the new UI file to the project.')

# (Groq client initialized earlier above; duplicate initialization removed)

# Custom CSS for modern dark chat theme
st.markdown("""
<style>
    [data-testid="stMainBlockContainer"] {
        background: #12131a;
        color: #e6e8ff;
    }
    
    [data-testid="stAppViewContainer"] {
        background: #12131a;
    }
    
    .main {
        background: #12131a;
    }
    
    .stSidebar {
        background: #1c1f2a;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    
    .header-container {
        background: #1f2331;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.2);
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .header-logo {
        width: 50px;
        height: 50px;
        background: #ffffff;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: #12131a;
        font-weight: bold;
    }
    
    .header-text {
        display: flex;
        flex-direction: column;
    }
    
    .header-title {
        font-size: 20px;
        font-weight: bold;
        color: #f8f9ff;
    }
    
    .header-subtitle {
        font-size: 12px;
        color: #9aa4ff;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .header-right {
        font-size: 12px;
        color: #cfd7ff;
    }

    .sidebar-card {
        background: #1b2030;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 18px;
        margin-bottom: 18px;
    }

    .sidebar-title {
        font-size: 13px;
        font-weight: 700;
        color: #eef2ff;
        margin-bottom: 10px;
    }

    .sidebar-text {
        font-size: 12px;
        color: #8f9bd2;
        line-height: 1.7;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        color: #c5d2ff;
        font-size: 11px;
    }
    
    .chat-container {
        min-height: 540px;
        max-height: 72vh;
        overflow-y: auto;
        padding: 24px;
        background: linear-gradient(180deg, #161928 0%, #1f2435 100%);
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        margin: 20px 0;
        box-shadow: 0 12px 50px rgba(0, 0, 0, 0.3);
    }
    
    .chat-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
    }
    
    .chat-title {
        font-size: 18px;
        font-weight: 700;
        color: #eef2ff;
        margin: 0;
    }
    
    .chat-subtitle {
        font-size: 12px;
        color: #92a4f5;
    }
    
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 320px;
        color: #b9c2ff;
        text-align: center;
    }
    
    .message {
        position: relative;
        margin-bottom: 18px;
        max-width: 72%;
        word-wrap: break-word;
        border-radius: 22px;
        padding: 18px 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
        line-height: 1.65;
    }
    
    .message-author {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        margin-bottom: 8px;
        color: #96a1ff;
    }
    
    .user-message {
        background: #f8f9ff;
        color: #12131a;
        margin-left: auto;
        text-align: right;
        border: 1px solid rgba(255,255,255,0.16);
    }
    
    .bot-message {
        background: rgba(255,255,255,0.05);
        color: #e6e8ff;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    .message strong {
        color: inherit;
    }
    
    .timestamp {
        font-size: 10px;
        color: #8f9bd2;
        margin-top: 10px;
    }
    
    .input-section {
        background: #1a1d2f;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 18px;
        display: flex;
        gap: 14px;
        align-items: center;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.22);
    }
    
    .input-field {
        flex: 1;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 16px;
        outline: none;
        background: #151829;
        color: #eef2ff;
        font-size: 14px;
    }
    
    .input-field::placeholder {
        color: #7b87c9;
    }
    
    .send-btn {
        background: #f8f9ff;
        border: none;
        border-radius: 18px;
        color: #12131a;
        padding: 14px 22px;
        cursor: pointer;
        font-weight: 700;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .send-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.16);
    }
    
    .mode-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .mode-btn {
        padding: 10px 18px;
        background: #f8f9ff;
        border: 1px solid rgba(18, 19, 26, 0.1);
        border-radius: 12px;
        color: #12131a;
        cursor: pointer;
        font-weight: 600;
    }
    
    .mode-btn.active {
        background: #ffffff;
        color: #12131a;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
    }
    
    .quick-actions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .quick-btn {
        padding: 12px 14px;
        background: #f8f9ff;
        border: 1px solid rgba(18, 19, 26, 0.1);
        border-radius: 12px;
        color: #12131a;
        cursor: pointer;
        font-weight: 600;
    }
    
    .quick-btn:hover {
        background: #ffffff;
    }

    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.04);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.16);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.24);
    }

    .stTextInput>div>div>input,
    .stTextInput>div>div>textarea {
        background: #141824 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 18px !important;
        color: #eef2ff !important;
        padding: 14px 16px !important;
    }

    .stTextInput>div>div>input::placeholder,
    .stTextInput>div>div>textarea::placeholder {
        color: #7b87c9 !important;
    }

    .stButton>button,
    button[data-baseweb="button"] {
        background: #f8f9ff !important;
        color: #12131a !important;
        border-radius: 18px !important;
        padding: 12px 20px !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.14) !important;
    }

    .stButton>button:hover,
    button[data-baseweb="button"]:hover {
        background: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# Database functions
def init_db():
    conn = sqlite3.connect('chat_history.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS messages
                    (id INTEGER PRIMARY KEY, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect('chat_history.db')
    conn.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def load_messages():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.execute("SELECT role, content, timestamp FROM messages ORDER BY id")
    messages = [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in cursor.fetchall()]
    conn.close()
    return messages

def clear_messages():
    conn = sqlite3.connect('chat_history.db')
    conn.execute("DELETE FROM messages")
    conn.commit()
    conn.close()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'mode' not in st.session_state:
    st.session_state.mode = "Casual"

if 'char_count' not in st.session_state:
    st.session_state.char_count = 0

if 'input' not in st.session_state:
    st.session_state.input = ""

if 'quick_prompt' not in st.session_state:
    st.session_state.quick_prompt = None

if 'error_message' not in st.session_state:
    st.session_state.error_message = None

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class='sidebar-card'>
        <div class='sidebar-title'>Astryx Controls</div>
        <div class='sidebar-text'>Use this panel to clear history and switch styles quickly. Astryx saves chat state only in your browser session.</div>
    </div>
    <div class='sidebar-card'>
        <div class='sidebar-title'>Quick Notes</div>
        <div class='sidebar-text'>Refresh the page after changing the `.env` key, and restart the app if the Groq key is invalid.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear History", use_container_width=True, key="clear_btn"):
        st.session_state.messages = []
        st.rerun()

# Main header
st.markdown("""
<div class="header-container">
    <div class="header-left">
        <div class="header-logo">⭐</div>
        <div class="header-text">
            <div class="header-title">ASTRYX</div>
            <div class="header-subtitle">Neural Interface</div>
        </div>
    </div>
    <div class="header-right">
        🟢 llama3-8b · groq
    </div>
</div>
""", unsafe_allow_html=True)

# Session init
st.markdown('<div class="session-init">- SESSION INIT -</div>', unsafe_allow_html=True)

# Chat container
chat_container = st.container()

with chat_container:
    st.markdown("""
    <div class='chat-head'>
        <div>
            <div class='chat-title'>Astryx Conversation</div>
            <div class='chat-subtitle'>AI chat, polished dark experience, session-only history.</div>
        </div>
        <div class='status-pill'>Online · Ready</div>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class='empty-state'>
            <div style='font-size: 14px; margin-bottom: 12px;'>System online. I'm Astryx — built on Groq's neural infrastructure.</div>
            <div style='font-size: 12px; color: #8f9bd2;'>Start the conversation with a single message.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            try:
                msg_time = datetime.fromisoformat(msg["timestamp"])
            except:
                msg_time = datetime.now()
            
            author = "You" if msg["role"] == "You" else "Astryx"
            bubble_class = "user-message" if msg["role"] == "You" else "bot-message"
            st.markdown(f"""
            <div class='message {bubble_class}'>
                <div class='message-author'>{author}</div>
                <div>{msg['content']}</div>
                <div class='timestamp'>{msg_time.strftime('%I:%M %p')}</div>
            </div>
            """, unsafe_allow_html=True)

# System mode selector
st.markdown('<div class="system-label">ASTRYX · SYSTEM</div>', unsafe_allow_html=True)

mode_cols = st.columns(3)
modes = ["Casual", "Precise", "Creative"]

for idx, mode in enumerate(modes):
    with mode_cols[idx]:
        if st.button(mode, use_container_width=True, key=f"mode_{mode}"):
            st.session_state.mode = mode
            st.rerun()

# Quick actions
st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
quick_col1, quick_col2 = st.columns(2)

quick_actions = [
    ("🌤️ Weather in Bengaluru", "What's the current weather in Bengaluru?"),
    ("🐛 Debug code", "Help me debug this code issue"),
    ("🎲 Surprise me", "Tell me something interesting and unexpected"),
    ("🌌 Quantum explained", "Explain quantum computing in simple terms")
]

for idx, (btn_text, prompt) in enumerate(quick_actions):
    if idx < 2:
        col = quick_col1
    else:
        col = quick_col2
    
    with col:
        if st.button(btn_text, use_container_width=True, key=f"quick_{idx}"):
            st.session_state.quick_prompt = prompt

def build_prompt(user_input: str) -> str:
    if st.session_state.mode == "Casual":
        return f"Respond in a casual, friendly, and relaxed way: {user_input}"
    elif st.session_state.mode == "Precise":
        return f"Respond in a precise, technical, and professional way: {user_input}"
    else:
        return f"Respond in a creative, imaginative, and innovative way: {user_input}"


def send_message():
    user_input = st.session_state.input.strip()
    if not user_input:
        return

    prompt = build_prompt(user_input)
    try:
        with st.spinner("⚡ Astryx processing..."):
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            bot_response = response.choices[0].message.content

        st.session_state.messages.append({"role": "You", "content": user_input, "timestamp": datetime.now().isoformat()})
        st.session_state.messages.append({"role": "Astryx", "content": bot_response, "timestamp": datetime.now().isoformat()})
        st.session_state.input = ""
        st.session_state.error_message = None
    except Exception as e:
        st.session_state.error_message = str(e)


# Input section
st.markdown("---")

if st.session_state.quick_prompt:
    st.session_state.input = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

with st.form(key="chat_form"):
    col1, col2 = st.columns([0.85, 0.15])

    with col1:
        user_input = st.text_input(
            "Message",
            value=st.session_state.input,
            placeholder="transmit a message...",
            key="input",
            max_chars=500,
            label_visibility="collapsed"
        )
        char_display = f"{len(user_input)}/500"

    with col2:
        st.markdown(f'<div class="char-counter">{char_display}</div>', unsafe_allow_html=True)
        st.form_submit_button("➤", key="send_btn", help="Send message", on_click=send_message, use_container_width=True)

if st.session_state.error_message:
    st.error(f"⚠️ Error: {st.session_state.error_message}")