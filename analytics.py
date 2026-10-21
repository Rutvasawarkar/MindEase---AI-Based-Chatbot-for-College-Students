import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from emotion_engine import EMOTION_COLORS, compute_burnout_score
from database import get_emotion_history, get_preferred_strategies
 
def build_emotion_timeline(user_id: int, days: int = 7) -> go.Figure:
    history = get_emotion_history(user_id, days)
    if not history:
        fig = go.Figure()
        fig.add_annotation(text="No emotion data yet. Start chatting!", 
                          xref="paper", yref="paper", x=0.5, y=0.5,
                          showarrow=False, font=dict(size=16, color="#94A3B8"))
        fig.update_layout(_dark_layout(f"Emotion Trend — Last {days} Days"))
        return fig
 
    df = pd.DataFrame(history)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
 
    # Emotion over time scatter
    emotion_list = list(EMOTION_COLORS.keys())
    df["emotion_idx"] = df["emotion"].apply(
        lambda e: emotion_list.index(e) if e in emotion_list else len(emotion_list) // 2
    )
    df["color"] = df["emotion"].map(EMOTION_COLORS).fillna("#CBD5E1")
 
    fig = go.Figure()
    for emotion in df["emotion"].unique():
        edf = df[df["emotion"] == emotion]
        fig.add_trace(go.Scatter(
            x=edf["timestamp"],
            y=edf["emotion_idx"],
            mode="markers+lines",
            name=emotion.capitalize(),
            marker=dict(
                color=EMOTION_COLORS.get(emotion, "#CBD5E1"),
                size=12,
                line=dict(color="white", width=1.5)
            ),
            line=dict(color=EMOTION_COLORS.get(emotion, "#CBD5E1"), width=2, dash="dot"),
            hovertemplate=f"<b>{emotion.capitalize()}</b><br>%{{x|%b %d, %H:%M}}<extra></extra>",
        ))
 
    fig.update_layout(
        **_dark_layout(f"Emotion Timeline — Last {days} Days"),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(emotion_list))),
            ticktext=[e.capitalize() for e in emotion_list],
            gridcolor="#1E293B",
        ),
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center",
                    font=dict(color="#94A3B8")),
    )
    return fig
 
 
def build_burnout_gauge(user_id: int, days: int = 7) -> go.Figure:
    history = get_emotion_history(user_id, days)
    score = compute_burnout_score(history)
 
    color = "#34D399" if score < 30 else "#F59E0B" if score < 60 else "#EF4444"
    label = "Low Risk" if score < 30 else "Moderate Risk" if score < 60 else "High Risk"
 
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={"text": f"Burnout Risk — {label}", "font": {"color": "#E2E8F0", "size": 16}},
        number={"suffix": "%", "font": {"color": color, "size": 48}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569", "tickfont": {"color": "#94A3B8"}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#1E293B",
            "bordercolor": "#334155",
            "steps": [
                {"range": [0, 30], "color": "#064E3B"},
                {"range": [30, 60], "color": "#78350F"},
                {"range": [60, 100], "color": "#7F1D1D"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        **_dark_layout(""),
        height=300,
    )
    return fig, score, label
 
 
def build_emotion_pie(user_id: int, days: int = 7) -> go.Figure:
    history = get_emotion_history(user_id, days)
    if not history:
        fig = go.Figure()
        fig.add_annotation(text="No data yet", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(color="#94A3B8"))
        fig.update_layout(_dark_layout("Emotion Distribution"))
        return fig
 
    df = pd.DataFrame(history)
    counts = df["emotion"].value_counts().reset_index()
    counts.columns = ["emotion", "count"]
    counts["color"] = counts["emotion"].map(EMOTION_COLORS)
 
    fig = go.Figure(go.Pie(
        labels=[e.capitalize() for e in counts["emotion"]],
        values=counts["count"],
        marker=dict(colors=counts["color"].tolist(), line=dict(color="#0F172A", width=2)),
        hole=0.5,
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **_dark_layout("Emotion Distribution"),
        legend=dict(font=dict(color="#94A3B8"), orientation="v"),
        height=300,
    )
    return fig
 
 
def build_daily_burnout_trend(user_id: int, days: int = 14) -> go.Figure:
    history = get_emotion_history(user_id, days)
    if not history:
        fig = go.Figure()
        fig.add_annotation(text="No data yet — keep chatting to see trends!",
                          xref="paper", yref="paper", x=0.5, y=0.5,
                          showarrow=False, font=dict(size=14, color="#94A3B8"))
        fig.update_layout(_dark_layout("Daily Burnout Trend"))
        return fig
 
    df = pd.DataFrame(history)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
 
    # Calculate daily burnout
    daily_scores = []
    for date, group in df.groupby("date"):
        records = group.to_dict("records")
        score = compute_burnout_score(records)
        daily_scores.append({"date": date, "burnout": score})
 
    ddf = pd.DataFrame(daily_scores).sort_values("date")
 
    colors = ["#EF4444" if s >= 60 else "#F59E0B" if s >= 30 else "#34D399"
              for s in ddf["burnout"]]
 
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ddf["date"].astype(str),
        y=ddf["burnout"],
        marker=dict(color=colors, line=dict(color="#0F172A", width=1)),
        hovertemplate="<b>%{x}</b><br>Burnout: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=60, line_dash="dash", line_color="#EF4444",
                 annotation_text="High Risk", annotation_font_color="#EF4444")
    fig.add_hline(y=30, line_dash="dash", line_color="#F59E0B",
                 annotation_text="Moderate Risk", annotation_font_color="#F59E0B")
    fig.update_layout(
        **_dark_layout(f"Daily Burnout Trend — Last {days} Days"),
        yaxis=dict(range=[0, 100], title="Burnout %", gridcolor="#1E293B",
                  titlefont=dict(color="#94A3B8"), tickfont=dict(color="#94A3B8")),
        xaxis=dict(gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
    )
    return fig
 
 
def build_strategy_chart(user_id: int) -> go.Figure:
    prefs = get_preferred_strategies(user_id)
    if not prefs:
        fig = go.Figure()
        fig.add_annotation(text="No strategy data yet",
                          xref="paper", yref="paper", x=0.5, y=0.5,
                          showarrow=False, font=dict(color="#94A3B8"))
        fig.update_layout(_dark_layout("Most Used Coping Strategies"))
        return fig
 
    strategies = list(prefs.keys())
    counts = list(prefs.values())
 
    # Strip emoji for cleaner display
    clean = [s[2:].strip() if len(s) > 2 and not s[1].isalpha() else s for s in strategies]
 
    fig = go.Figure(go.Bar(
        y=clean, x=counts, orientation="h",
        marker=dict(
            color=["#6366F1", "#8B5CF6", "#A78BFA", "#C4B5FD", "#DDD6FE"][:len(counts)],
            line=dict(color="#0F172A", width=1),
        ),
        hovertemplate="<b>%{y}</b><br>Used: %{x} times<extra></extra>",
    ))
    fig.update_layout(
        **_dark_layout("Your Most Used Coping Strategies"),
        xaxis=dict(title="Times Selected", gridcolor="#1E293B",
                  titlefont=dict(color="#94A3B8"), tickfont=dict(color="#94A3B8")),
        yaxis=dict(gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
        height=max(200, len(strategies) * 50),
    )
    return fig
 
 
def get_weekly_summary(user_id: int) -> dict:
    history_7 = get_emotion_history(user_id, 7)
    history_1 = get_emotion_history(user_id, 1)
 
    if not history_7:
        return {"total_checkins": 0, "burnout_7d": 0, "burnout_1d": 0,
                "top_emotion": "—", "mood_trend": "neutral"}
 
    df = pd.DataFrame(history_7)
    top = df["emotion"].value_counts().idxmax() if not df.empty else "—"
 
    b7 = compute_burnout_score(history_7)
    b1 = compute_burnout_score(history_1)
    trend = "improving" if b1 < b7 - 5 else "worsening" if b1 > b7 + 5 else "stable"
 
    return {
        "total_checkins": len(history_7),
        "burnout_7d": b7,
        "burnout_1d": b1,
        "top_emotion": top.capitalize(),
        "mood_trend": trend,
    }
 
 
def _dark_layout(title: str) -> dict:
    return {
        "title": {"text": title, "font": {"color": "#E2E8F0", "size": 15}, "x": 0.5},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#94A3B8"},
        "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
    }
 