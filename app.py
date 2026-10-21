"""
MindEase — AI Mental Health Chatbot for Students
Main entry point. Run with: streamlit run app.py
"""
 
import streamlit as st
from pathlib import Path
import database as db
 
# ── Page config (must be first) ───────────────────────────────────────────────
st.set_page_config(
    page_title="MindEase · Student Mental Health",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Load CSS ──────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
 
# ── Init DB ───────────────────────────────────────────────────────────────────
db.init_db()
 
# ── Session state defaults ────────────────────────────────────────────────────
DEFAULTS = {
    "authenticated": False,
    "user": None,
    "page": "chat",
    "chat_history": [],
    "current_emotion": "neutral",
    "emotion_confidence": 0.5,
    "strategy_mode": False,
    "active_strategy": None,
    "strategy_step": 0,
    "strategy_context": {},
    "pending_strategies": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v
 
# ── Route to pages ────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    from pages.auth_page import render_auth
    render_auth()
elif st.session_state.page == "analytics":
    from pages.analytics_page import render_analytics
    render_analytics()
else:
    from pages.chat_page import render_chat
    render_chat()