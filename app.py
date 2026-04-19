import streamlit as st
import os
from dotenv import load_dotenv
import groq
import sqlite3
from datetime import datetime
from datetime import date as date_module

# Page config
st.set_page_config(page_title="Astryx - Neural Interface", layout="wide")

# Load environment variables
load_dotenv('.env')

# Groq configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')

if not GROQ_API_KEY:
    st.error("Error: GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

client = groq.Groq(api_key=GROQ_API_KEY)

# Custom CSS for cyberpunk theme
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stMainBlockContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 100%);
        color: #e0e0ff;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 100%);
    }
    
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 100%);
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #1a1f4a 0%, #0f1230 100%);
        border-right: 2px solid #4a5aff;
    }
    
    .header-container {
        background: rgba(20, 20, 50, 0.8);
        border: 2px solid #4a5aff;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .header-logo {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #7c5aff 0%, #4a9aff 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    
    .header-text {
        display: flex;
        flex-direction: column;
    }
    
    .header-title {
        font-size: 18px;
        font-weight: bold;
        color: #fff;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .header-subtitle {
        font-size: 11px;
        color: #7c5aff;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .header-right {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 11px;
        color: #7c9aff;
        background: rgba(100, 120, 255, 0.1);
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid rgba(100, 120, 255, 0.3);
    }
    
    .session-init {
        text-align: center;
        color: #666;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 20px 0;
    }
    
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 20px;
        margin: 20px 0;
    }
    
    .message-group {
        margin-bottom: 20px;
        animation: slideIn 0.3s ease-in;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .bot-message {
        display: flex;
        gap: 12px;
        margin-bottom: 15px;
    }
    
    .user-message {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-bottom: 15px;
    }
    
    .message-bubble {
        max-width: 65%;
        padding: 14px 16px;
        border-radius: 8px;
        font-size: 13px;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .bot-bubble {
        background: rgba(70, 100, 200, 0.15);
        border: 1px solid rgba(100, 150, 255, 0.4);
        border-left: 3px solid #4a7aff;
        color: #e0e0ff;
    }
    
    .user-bubble {
        background: rgba(150, 100, 200, 0.2);
        border: 1px solid rgba(150, 100, 255, 0.4);
        border-left: 3px solid #9a6aff;
        color: #fff;
    }
    
    .timestamp {
        font-size: 10px;
        color: #666;
        margin-top: 6px;
    }
    
    .system-label {
        text-align: center;
        color: #666;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 15px 0 10px 0;
    }
    
    .mode-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
        flex-wrap: wrap;
    }
    
    .mode-btn {
        padding: 8px 16px;
        background: transparent;
        border: 1px solid rgba(200, 150, 255, 0.4);
        border-radius: 6px;
        color: #c896ff;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .mode-btn.active {
        background: rgba(200, 150, 255, 0.2);
        border-color: #9a6aff;
        color: #fff;
        box-shadow: 0 0 10px rgba(150, 100, 255, 0.3);
    }
    
    .quick-actions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 15px;
    }
    
    .quick-btn {
        padding: 10px 12px;
        background: transparent;
        border: 1px solid rgba(100, 150, 255, 0.3);
        border-radius: 6px;
        color: #7c9aff;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .quick-btn:hover {
        background: rgba(100, 150, 255, 0.1);
        border-color: #4a9aff;
        color: #fff;
        box-shadow: 0 0 8px rgba(100, 150, 255, 0.2);
    }
    
    .input-section {
        background: rgba(20, 20, 50, 0.5);
        border: 1px solid rgba(100, 150, 255, 0.3);
        border-radius: 6px;
        padding: 12px;
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .input-field {
        flex: 1;
        background: transparent;
        border: none;
        color: #e0e0ff;
        outline: none;
        font-size: 13px;
    }
    
    .char-counter {
        font-size: 10px;
        color: #666;
        text-transform: uppercase;
    }
    
    .send-btn {
        background: linear-gradient(135deg, #7c5aff 0%, #4a9aff 100%);
        border: none;
        border-radius: 6px;
        color: #fff;
        padding: 8px 12px;
        cursor: pointer;
        font-size: 16px;
        transition: all 0.3s;
    }
    
    .send-btn:hover {
        box-shadow: 0 0 15px rgba(100, 150, 255, 0.5);
        transform: translateY(-2px);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(100, 150, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #7c5aff 0%, #4a9aff 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #6c4aef 0%, #3a8aef 100%);
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
    init_db()
    st.session_state.messages = load_messages()

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
    <div style="padding: 20px 0;">
        <div style="height: 40px; background: rgba(100, 150, 255, 0.1); border: 1px solid rgba(100, 150, 255, 0.3); border-radius: 8px; margin-bottom: 10px;"></div>
        <div style="height: 40px; background: rgba(100, 150, 255, 0.1); border: 1px solid rgba(100, 150, 255, 0.3); border-radius: 8px; margin-bottom: 10px;"></div>
        <div style="height: 40px; background: rgba(100, 150, 255, 0.1); border: 1px solid rgba(100, 150, 255, 0.3); border-radius: 8px; margin-bottom: 10px;"></div>
        <div style="height: 40px; background: rgba(100, 150, 255, 0.1); border: 1px solid rgba(100, 150, 255, 0.3); border-radius: 8px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear History", use_container_width=True, key="clear_btn"):
        clear_messages()
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
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 80px 20px; font-size: 13px;">
            System online. I'm Astryx — built on Groq's neural infrastructure.<br>
            No fluff, no limits. What do you want to explore?
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            try:
                msg_time = datetime.fromisoformat(msg["timestamp"])
            except:
                msg_time = datetime.now()
            
            if msg["role"] == "You":
                st.markdown(f"""
                <div class='user-message'>
                    <div class='message-bubble user-bubble'>
                        {msg['content']}
                        <div class='timestamp'>{msg_time.strftime('%I:%M %p')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='bot-message'>
                    <div class='message-bubble bot-bubble'>
                        {msg['content']}
                        <div class='timestamp'>{msg_time.strftime('%I:%M %p')}</div>
                    </div>
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
        save_message("You", user_input)
        st.session_state.messages.append({"role": "Astryx", "content": bot_response, "timestamp": datetime.now().isoformat()})
        save_message("Astryx", bot_response)
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