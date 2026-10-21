import streamlit as st
import database as db
import re
 
 
def render_auth():
    # Center the auth card
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 40px 0 32px;">
            <div style="font-size:3rem; margin-bottom:8px;">🧠</div>
            <h1 style="font-size:2.2rem; font-weight:800;
                background: linear-gradient(135deg, #6366F1, #A78BFA, #34D399);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip:text; margin:0; letter-spacing:-1px;">MindEase</h1>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:8px;">
                Your AI companion for student mental wellness
            </p>
        </div>
        """, unsafe_allow_html=True)
 
        tab_login, tab_signup = st.tabs(["🔑  Sign In", "✨  Create Account"])
 
        # ── LOGIN ──────────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
 
            if st.button("Sign In →", use_container_width=True, key="btn_login"):
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    user = db.verify_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.chat_history = db.get_chat_history(user["id"])
                        st.success(f"Welcome back, {user['username']}! 👋")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
 
            st.markdown("""
            <div style="text-align:center; margin-top:24px; color:#475569; font-size:0.8rem;">
                Your conversations are private and secure 🔒
            </div>
            """, unsafe_allow_html=True)
 
        # ── SIGNUP ─────────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            new_username = st.text_input("Username", placeholder="Choose a username", key="signup_user")
            new_email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
            new_pass = st.text_input("Password", type="password", placeholder="Create a password (min 6 chars)", key="signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="signup_confirm")
            st.markdown("<br>", unsafe_allow_html=True)
 
            if st.button("Create Account →", use_container_width=True, key="btn_signup"):
                errors = _validate_signup(new_username, new_email, new_pass, confirm_pass)
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    ok, msg = db.create_user(new_username, new_email, new_pass)
                    if ok:
                        st.success(f"Account created! Welcome to MindEase, {new_username} 🎉")
                        st.info("Please switch to the Sign In tab to log in.")
                    else:
                        st.error(msg)
 
            st.markdown("""
            <div style="text-align:center; margin-top:24px; padding: 16px;
                background: rgba(99,102,241,0.08); border-radius: 12px;
                border: 1px solid rgba(99,102,241,0.2);">
                <p style="color:#94A3B8; font-size:0.82rem; margin:0;">
                    🌱 MindEase uses AI to help you track emotions, detect burnout,
                    and discover personalized coping strategies — built specifically for students.
                </p>
            </div>
            """, unsafe_allow_html=True)
 
 
def _validate_signup(username, email, password, confirm):
    errors = []
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email or ""):
        errors.append("Please enter a valid email address.")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")
    return errors
 