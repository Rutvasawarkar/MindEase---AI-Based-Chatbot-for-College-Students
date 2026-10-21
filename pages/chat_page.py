import streamlit as st
from datetime import datetime
import database as db
from emotion_engine import detect_emotion, emotion_display, EMOTION_COLORS, compute_burnout_score
from coping_engine import (
    get_empathy_opener, get_strategies_for_emotion, get_strategy_step,
    is_greeting, get_greeting_response, get_general_response,
    crisis_check, CRISIS_RESPONSE
)
 
 
def render_chat():
    user = st.session_state.user
    user_id = user["id"]
 
    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            <div style="font-size:1.8rem;">🧠</div>
            <h2>MindEase</h2>
            <p style="color:#64748B; font-size:0.75rem; margin:0;">Student Mental Wellness</p>
        </div>
        <div class="sidebar-user">
            👤 &nbsp; <b style="color:#F1F5F9;">{user['username']}</b>
        </div>
        """, unsafe_allow_html=True)
 
        # Current emotion display
        emotion = st.session_state.current_emotion
        color = EMOTION_COLORS.get(emotion, "#CBD5E1")
        conf = int(st.session_state.emotion_confidence * 100)
        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <p style="color:#64748B; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">
                Current Emotion
            </p>
            <div style="background:rgba(0,0,0,0.2); border:1px solid {color}33;
                border-radius:10px; padding:12px 16px; text-align:center;">
                <div style="font-size:1.8rem; margin-bottom:4px;">{_emotion_emoji(emotion)}</div>
                <div style="font-weight:700; color:{color}; font-size:1rem;">{emotion.capitalize()}</div>
                <div style="color:#64748B; font-size:0.75rem; margin-top:2px;">Confidence: {conf}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
        # Quick burnout meter
        recent = db.get_emotion_history(user_id, 7)
        burnout = compute_burnout_score(recent)
        burnout_color = "#34D399" if burnout < 30 else "#F59E0B" if burnout < 60 else "#EF4444"
        burnout_label = "Low" if burnout < 30 else "Moderate" if burnout < 60 else "High"
        st.markdown(f"""
        <div style="margin-bottom:20px;">
            <p style="color:#64748B; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">
                7-Day Burnout Risk
            </p>
            <div style="background:rgba(0,0,0,0.2); border:1px solid {burnout_color}33;
                border-radius:10px; padding:12px 16px; text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:{burnout_color};">{burnout:.0f}%</div>
                <div style="color:#64748B; font-size:0.75rem;">{burnout_label} Risk</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
        st.markdown("---")
 
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
 
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.strategy_mode = False
            st.session_state.active_strategy = None
            st.session_state.strategy_step = 0
            st.rerun()
 
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
 
        st.markdown("""
        <div style="margin-top:16px; padding:12px; background:rgba(99,102,241,0.08);
            border-radius:10px; border:1px solid rgba(99,102,241,0.15);">
            <p style="color:#64748B; font-size:0.72rem; margin:0; line-height:1.5;">
                🆘 <b style="color:#94A3B8;">Crisis Helpline</b><br>
                iCall: <b style="color:#F1F5F9;">9152987821</b><br>
                Vandrevala: <b style="color:#F1F5F9;">1860-2662-345</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
 
    # ── Main Chat Area ─────────────────────────────────────────────────────────
    st.markdown("""
    <h1 style="font-size:1.5rem; font-weight:700; margin:0 0 4px 0;
        background:linear-gradient(135deg,#6366F1,#A78BFA);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-clip:text;">
        Chat with MindEase 💬
    </h1>
    <p style="color:#64748B; font-size:0.85rem; margin:0 0 20px 0;">
        Share what's on your mind — I'm here to listen and help.
    </p>
    """, unsafe_allow_html=True)
 
    # ── Strategy selection panel ───────────────────────────────────────────────
    if st.session_state.pending_strategies and not st.session_state.strategy_mode:
        _render_strategy_selector(user_id)
    else:
        # ── Chat messages ──────────────────────────────────────────────────────
        _render_messages()
 
        # ── Input bar ──────────────────────────────────────────────────────────
        _render_input_bar(user_id)
 
 
def _render_messages():
    history = st.session_state.chat_history
    if not history:
        st.markdown("""
        <div style="display:flex; flex-direction:column; align-items:center;
            justify-content:center; height:400px; gap:12px; color:#475569;">
            <div style="font-size:3rem;">🌱</div>
            <div style="font-size:1rem; font-weight:600; color:#64748B;">How are you feeling today?</div>
            <div style="font-size:0.85rem; color:#475569; text-align:center; max-width:300px; line-height:1.5;">
                Start by sharing what's on your mind. I'll listen, understand, and help you cope.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
 
    # Render chat bubble HTML
    bubbles_html = '<div class="chat-area" id="chat-scroll">'
    for msg in history:
        role = msg.get("role", "bot")
        content = msg.get("content", "")
        ts = msg.get("timestamp", "")
        if ts:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(ts)
                ts_display = dt.strftime("%I:%M %p")
            except:
                ts_display = ts[-8:-3] if len(ts) >= 8 else ts
        else:
            ts_display = ""
 
        css_class = "user" if role == "user" else "bot"
        # Escape HTML in content, but allow markdown-ish bold
        safe_content = content.replace("<", "&lt;").replace(">", "&gt;")
        # Convert **bold** -> <b>
        import re
        safe_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_content)
        safe_content = safe_content.replace("\n", "<br>")
 
        bubbles_html += f"""
        <div class="msg-row {css_class}">
            <div>
                <div class="msg-bubble {css_class}">{safe_content}</div>
                <div class="msg-meta">{ts_display}</div>
            </div>
        </div>"""
 
    bubbles_html += '</div>'
    bubbles_html += """
    <script>
        var el = document.getElementById('chat-scroll');
        if(el) el.scrollTop = el.scrollHeight;
    </script>"""
 
    st.markdown(bubbles_html, unsafe_allow_html=True)
 
 
def _render_input_bar(user_id: int):
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "message",
            placeholder="Type how you're feeling...",
            label_visibility="collapsed",
            key="chat_input_field",
        )
    with col_send:
        send_clicked = st.button("Send ➤", use_container_width=True)
 
    if send_clicked and user_input and user_input.strip():
        _process_message(user_id, user_input.strip())
        # Clear input by rerunning
        st.rerun()
 
 
def _process_message(user_id: int, text: str):
    now = datetime.now().isoformat()
 
    # Crisis check first
    if crisis_check(text):
        _add_message(user_id, "user", text, now)
        _add_message(user_id, "bot", CRISIS_RESPONSE, now, "stress")
        db.log_emotion(user_id, "stress", 80)
        return
 
    # Detect emotion
    emotion, confidence = detect_emotion(text)
    st.session_state.current_emotion = emotion
    st.session_state.emotion_confidence = confidence
    db.log_emotion(user_id, emotion, compute_burnout_score(db.get_emotion_history(user_id, 7)))
 
    # Save user message
    _add_message(user_id, "user", text, now, emotion)
 
    # Build bot response
    if st.session_state.strategy_mode and st.session_state.active_strategy:
        _handle_strategy_step(user_id, text, emotion, now)
    elif is_greeting(text):
        response = get_greeting_response(st.session_state.user["username"])
        _add_message(user_id, "bot", response, now)
    else:
        # First response: empathy opener
        opener = get_empathy_opener(emotion)
        prefs = db.get_preferred_strategies(user_id)
        strategies = get_strategies_for_emotion(emotion, prefs)
 
        response = f"{opener}\n\nBased on what you've shared, here are some strategies that might help. **Please select one below** and I'll guide you through it step-by-step."
        _add_message(user_id, "bot", response, now, emotion)
 
        # Store pending strategies
        st.session_state.pending_strategies = strategies[:4]
        st.session_state.current_emotion_for_strategy = emotion
 
 
def _handle_strategy_step(user_id: int, user_text: str, emotion: str, now: str):
    strategy_id = st.session_state.active_strategy
    step = st.session_state.strategy_step
    context = st.session_state.strategy_context
 
    # Store user input as context for dynamic steps
    if step == 1:
        context["task"] = user_text[:50]
        st.session_state.strategy_context = context
 
    step += 1
    st.session_state.strategy_step = step
 
    next_step = get_strategy_step(
        strategy_id,
        st.session_state.get("current_emotion_for_strategy", emotion),
        step,
        context
    )
 
    if next_step:
        _add_message(user_id, "bot", next_step, now, emotion)
    
    # Check if we've reached the end naturally
    all_strategies = []
    from coping_engine import STRATEGIES
    for s_list in STRATEGIES.values():
        all_strategies.extend(s_list)
    
    for s in all_strategies:
        if s["id"] == strategy_id:
            if step >= len(s["steps"]):
                # Strategy complete
                completion = (
                    "\n\n✅ **Great work completing this exercise!** "
                    "How are you feeling now compared to before? "
                    "Feel free to keep chatting, or type 'strategies' to explore another coping technique."
                )
                _add_message(user_id, "bot", completion, now)
                st.session_state.strategy_mode = False
                st.session_state.active_strategy = None
                st.session_state.strategy_step = 0
            break
 
 
def _render_strategy_selector(user_id: int):
    strategies = st.session_state.pending_strategies
    emotion = st.session_state.get("current_emotion_for_strategy", "neutral")
    color = EMOTION_COLORS.get(emotion, "#6366F1")
 
    st.markdown(f"""
    <div style="background:var(--bg-surface); border:1px solid {color}33;
        border-radius:16px; padding:24px; margin-bottom:16px;">
        <h3 style="color:#F1F5F9; font-size:1rem; font-weight:700; margin:0 0 6px 0;">
            💡 Choose a Coping Strategy
        </h3>
        <p style="color:#64748B; font-size:0.83rem; margin:0 0 20px 0;">
            Select one and I'll guide you through it interactively.
        </p>
    </div>
    """, unsafe_allow_html=True)
 
    cols = st.columns(2)
    for i, strategy in enumerate(strategies):
        with cols[i % 2]:
            card_html = f"""
            <div style="background:#1E293B; border:1px solid #334155; border-radius:14px;
                padding:16px; margin-bottom:8px; border-left:3px solid {color};">
                <div style="font-weight:700; font-size:0.95rem; color:#F1F5F9; margin-bottom:6px;">
                    {strategy['title']}
                </div>
                <div style="color:#94A3B8; font-size:0.82rem; line-height:1.4;">
                    {strategy['desc']}
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"Choose This →", key=f"strategy_{i}", use_container_width=True):
                _select_strategy(user_id, strategy, emotion)
                st.rerun()
 
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Skip — Just Chat", key="skip_strategy"):
        st.session_state.pending_strategies = []
        st.rerun()
 
 
def _select_strategy(user_id: int, strategy: dict, emotion: str):
    # Save selection to DB for adaptive learning
    db.save_strategy(user_id, strategy["title"], emotion)
 
    st.session_state.strategy_mode = True
    st.session_state.active_strategy = strategy["id"]
    st.session_state.strategy_step = 0
    st.session_state.strategy_context = {}
    st.session_state.pending_strategies = []
    st.session_state.current_emotion_for_strategy = emotion
 
    now = datetime.now().isoformat()
    first_step = get_strategy_step(strategy["id"], emotion, 0)
    intro = f"✨ Let's work through **{strategy['title']}** together.\n\n{first_step}"
    _add_message(user_id, "bot", intro, now, emotion)
 
 
def _add_message(user_id: int, role: str, content: str, timestamp: str, emotion: str = None):
    msg = {"role": role, "content": content, "timestamp": timestamp, "emotion": emotion}
    st.session_state.chat_history.append(msg)
    db.save_message(user_id, role, content, emotion)
 
 
def _emotion_emoji(emotion: str) -> str:
    emojis = {
        "stress": "😰", "fatigue": "😴", "anxiety": "😟",
        "overthinking": "🌀", "calm": "😌", "motivation": "🚀",
        "sadness": "😢", "neutral": "😐"
    }
    return emojis.get(emotion, "💭")
 