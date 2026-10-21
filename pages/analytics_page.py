import streamlit as st
from analytics import (
    build_emotion_timeline, build_burnout_gauge,
    build_emotion_pie, build_daily_burnout_trend,
    build_strategy_chart, get_weekly_summary
)
from emotion_engine import EMOTION_COLORS
import database as db
 
 
def render_analytics():
    user = st.session_state.user
    user_id = user["id"]
 
    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            <div style="font-size:1.8rem;">📊</div>
            <h2>Analytics</h2>
            <p style="color:#64748B; font-size:0.75rem; margin:0;">Your Wellness Report</p>
        </div>
        <div class="sidebar-user">
            👤 &nbsp; <b style="color:#F1F5F9;">{user['username']}</b>
        </div>
        """, unsafe_allow_html=True)
 
        st.markdown("---")
        if st.button("💬 Back to Chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
 
        st.markdown("<br>", unsafe_allow_html=True)
 
        # Time range selector
        st.markdown("<p style='color:#64748B; font-size:0.8rem; margin-bottom:8px;'>📅 Time Range</p>",
                   unsafe_allow_html=True)
        time_range = st.radio(
            "time_range",
            options=["Last 7 Days", "Last 14 Days", "Last 30 Days"],
            label_visibility="collapsed",
        )
        days = {"Last 7 Days": 7, "Last 14 Days": 14, "Last 30 Days": 30}[time_range]
 
        if st.button("🚪 Sign Out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
 
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <h1 style="font-size:1.6rem; font-weight:800; margin:0 0 4px 0;
        background:linear-gradient(135deg,#6366F1,#A78BFA,#34D399);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-clip:text;">
        Wellness Analytics 📊
    </h1>
    <p style="color:#64748B; font-size:0.85rem; margin:0 0 24px 0;">
        Track your emotional patterns, burnout risk, and coping progress.
    </p>
    """, unsafe_allow_html=True)
 
    # ── Summary Cards ─────────────────────────────────────────────────────────
    summary = get_weekly_summary(user_id)
    
    trend_icon = {"improving": "📈", "worsening": "📉", "stable": "➡️"}.get(summary["mood_trend"], "➡️")
    trend_color = {"improving": "#34D399", "worsening": "#EF4444", "stable": "#94A3B8"}.get(summary["mood_trend"])
    burnout_color = "#34D399" if summary["burnout_7d"] < 30 else "#F59E0B" if summary["burnout_7d"] < 60 else "#EF4444"
 
    c1, c2, c3, c4 = st.columns(4)
    _metric_card(c1, str(summary["total_checkins"]), "Check-ins (7d)", "💬")
    _metric_card(c2, f"{summary['burnout_7d']:.0f}%", "Burnout Score", "🔥", burnout_color)
    _metric_card(c3, summary["top_emotion"], "Top Emotion (7d)", "🎭")
    _metric_card(c4, f"{trend_icon} {summary['mood_trend'].capitalize()}", "Mood Trend", "📊", trend_color)
 
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
 
    # ── Burnout Gauge ──────────────────────────────────────────────────────────
    st.markdown("""
    <h2 style="color:#F1F5F9; font-size:1.1rem; font-weight:700; margin-bottom:12px;">
        🔥 Burnout Risk Assessment
    </h2>
    """, unsafe_allow_html=True)
 
    g_col1, g_col2 = st.columns([1, 2])
    with g_col1:
        fig_gauge, score, label = build_burnout_gauge(user_id, days)
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
 
    with g_col2:
        burnout_advice = _get_burnout_advice(score)
        b_color = "#34D399" if score < 30 else "#F59E0B" if score < 60 else "#EF4444"
        st.markdown(f"""
        <div style="background:#1E293B; border:1px solid {b_color}33; border-left:4px solid {b_color};
            border-radius:14px; padding:20px; height:100%; box-sizing:border-box; margin-top:8px;">
            <div style="font-size:1.8rem; margin-bottom:8px;">{burnout_advice['icon']}</div>
            <h3 style="color:{b_color}; font-size:1rem; font-weight:700; margin:0 0 8px 0;">
                {label} — {score:.1f}% Burnout
            </h3>
            <p style="color:#94A3B8; font-size:0.85rem; line-height:1.6; margin:0;">
                {burnout_advice['message']}
            </p>
        </div>
        """, unsafe_allow_html=True)
 
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
 
    # ── Daily Burnout Trend ────────────────────────────────────────────────────
    st.markdown(f"""
    <h2 style="color:#F1F5F9; font-size:1.1rem; font-weight:700; margin-bottom:12px;">
        📈 Daily Burnout Trend
    </h2>
    """, unsafe_allow_html=True)
    fig_trend = build_daily_burnout_trend(user_id, days)
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
 
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
 
    # ── Emotion Timeline ───────────────────────────────────────────────────────
    st.markdown("""
    <h2 style="color:#F1F5F9; font-size:1.1rem; font-weight:700; margin-bottom:12px;">
        🎭 Emotion Timeline
    </h2>
    """, unsafe_allow_html=True)
    fig_timeline = build_emotion_timeline(user_id, days)
    st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
 
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
 
    # ── Pie + Strategy side by side ────────────────────────────────────────────
    pie_col, strat_col = st.columns(2)
 
    with pie_col:
        st.markdown("""
        <h2 style="color:#F1F5F9; font-size:1.1rem; font-weight:700; margin-bottom:12px;">
            🥧 Emotion Distribution
        </h2>""", unsafe_allow_html=True)
        fig_pie = build_emotion_pie(user_id, days)
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
 
    with strat_col:
        st.markdown("""
        <h2 style="color:#F1F5F9; font-size:1.1rem; font-weight:700; margin-bottom:12px;">
            💡 Your Top Coping Strategies
        </h2>""", unsafe_allow_html=True)
        fig_strat = build_strategy_chart(user_id)
        st.plotly_chart(fig_strat, use_container_width=True, config={"displayModeBar": False})
 
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
 
    # ── Recent Emotion Log ─────────────────────────────────────────────────────
    with st.expander("📋 Recent Emotion Log", expanded=False):
        history = db.get_emotion_history(user_id, days)
        if not history:
            st.info("No emotion data yet. Start a conversation to begin tracking!")
        else:
            import pandas as pd
            df = pd.DataFrame(history)[["timestamp", "emotion", "burnout_score"]]
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%b %d, %H:%M")
            df.columns = ["Time", "Emotion", "Burnout Score"]
            df["Emotion"] = df["Emotion"].str.capitalize()
            df["Burnout Score"] = df["Burnout Score"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(df, use_container_width=True, hide_index=True)
 
    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; margin-top:32px; padding:20px;
        color:#334155; font-size:0.75rem; border-top:1px solid #1E293B;">
        MindEase — Built with care for student wellbeing 💙<br>
        Data is stored locally and privately on your device.
    </div>
    """, unsafe_allow_html=True)
 
 
def _metric_card(col, value: str, label: str, icon: str, color: str = "#6366F1"):
    with col:
        st.markdown(f"""
        <div style="background:#1E293B; border:1px solid #334155; border-radius:14px;
            padding:20px 16px; text-align:center; height:110px; display:flex;
            flex-direction:column; justify-content:center; gap:4px;">
            <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase;
                letter-spacing:0.08em;">{icon} {label}</div>
            <div style="font-size:1.6rem; font-weight:800; color:{color};
                letter-spacing:-1px; line-height:1;">{value}</div>
        </div>
        """, unsafe_allow_html=True)
 
 
def _get_burnout_advice(score: float) -> dict:
    if score < 30:
        return {
            "icon": "🌿",
            "message": (
                "You're in a healthy range. Your emotional balance is good. "
                "Keep maintaining your routines, sleep schedule, and social connections. "
                "These habits are your best prevention."
            )
        }
    elif score < 60:
        return {
            "icon": "⚠️",
            "message": (
                "You're showing moderate burnout signals. It's important to address this now "
                "before it escalates. Prioritize rest, reduce discretionary commitments where possible, "
                "and use the coping strategies regularly. Consider talking to a counselor."
            )
        }
    else:
        return {
            "icon": "🚨",
            "message": (
                "Your burnout risk is high. Please take this seriously. "
                "Reach out to your university's counseling services, a trusted friend, "
                "or a mental health professional. Rest is not optional — it's urgent. "
                "You deserve support."
            )
        }
 