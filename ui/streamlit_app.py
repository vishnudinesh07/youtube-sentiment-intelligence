import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="YouTube Sentiment Intelligence",
    layout="wide"
)

# ---------------------------------------------------
# LOAD CSS
# ---------------------------------------------------
def load_css():
    css_path = Path(__file__).parent / "styles.css"
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------------------------------------------
# TOP TICKER
# ---------------------------------------------------
st.markdown("""
<div class="ticker-wrap">
    <div class="ticker">
        Real-time YouTube audience intelligence • Multilingual sentiment detection • Live comment analytics • Executive insights • FastAPI powered • Streamlit premium dashboard • Instant reaction tracking • Audience mood engine
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.markdown("""
<div class="brand-wrap">
    <span class="youtube-pill">▶ YouTube</span>
    <span class="brand-title">Sentiment Intelligence</span>
</div>

<div class="subtitle">
Real-time audience perception and comment intelligence platform
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# INPUTS
# ---------------------------------------------------
col1, col2 = st.columns([5,1])

with col1:
    url = st.text_input("Video URL")

with col2:
    limit = st.selectbox("Limit", [100,125,150,175,200], index=0)

run = st.button("Analyse")

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
if run:

    try:
        with st.spinner("Analysing live audience sentiment..."):
            response = requests.post(
                "https://youtube-sentiment-intelligence.onrender.com/analyse",
                json={"url": url, "limit": limit},
                timeout=60
            )

        # -------------------------------------------
        # HANDLE API ERRORS
        # -------------------------------------------
        if response.status_code != 200:
            try:
                error_detail = response.json().get(
                    "detail",
                    "Unable to analyse video."
                )
            except Exception:
                error_detail = "Unable to analyse video."

            st.error(error_detail)
            st.stop()

        data = response.json()

    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        st.stop()

    except requests.exceptions.ConnectionError:
        st.error("Backend service unavailable.")
        st.stop()

    except requests.exceptions.RequestException:
        st.error("Network error occurred while contacting API.")
        st.stop()

    except Exception:
        st.error("Unexpected error occurred.")
        st.stop()

    # -------------------------------------------
    # NO COMMENTS CASE
    # -------------------------------------------
    if data["returned_comments"] == 0:
        st.warning("No public comments available for this video.")
        st.stop()

    summary = data["sentiment_summary"]
    meta = data["video_metadata"]
    execs = data["executive_summary"]

    overall = execs["overall_sentiment"].lower()

    if "positive" in overall:
        hero_color = "#22c55e"
    elif "negative" in overall:
        hero_color = "#ef4444"
    else:
        hero_color = "#f59e0b"

    # HERO
    st.markdown(f"""
    <div class="hero" style="
        border:1px solid {hero_color};
        box-shadow:0 14px 32px {hero_color}22;">
        <div class="small-label">Overall Sentiment</div>
        <div style="
            font-size:2.8rem;
            font-weight:800;
            color:{hero_color};
            margin-top:8px;">
            {execs["overall_sentiment"]}
        </div>
        <div class="small-label">{execs["audience_mood"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI
    c1,c2,c3,c4 = st.columns(4)

    metrics = [
        ("Positive", summary["positive_pct"]),
        ("Neutral", summary["neutral_pct"]),
        ("Negative", summary["negative_pct"]),
        ("Comments", data["returned_comments"])
    ]

    for col, item in zip([c1,c2,c3,c4], metrics):
        with col:
            suffix = "%" if item[0] != "Comments" else ""
            st.markdown(f"""
            <div class="card">
                <div class="small-label">{item[0]}</div>
                <div class="big-value">{item[1]}{suffix}</div>
            </div>
            """, unsafe_allow_html=True)

    # PROGRESS
    st.markdown(
        '<div class="progress-title">Positive Sentiment</div>',
        unsafe_allow_html=True
    )
    st.progress(int(summary["positive_pct"]))

    st.markdown(
        '<div class="progress-title">Neutral Sentiment</div>',
        unsafe_allow_html=True
    )
    st.progress(int(summary["neutral_pct"]))

    st.markdown(
        '<div class="progress-title">Negative Sentiment</div>',
        unsafe_allow_html=True
    )
    st.progress(int(summary["negative_pct"]))

    # VIDEO
    with st.expander("✦ Video Intelligence", expanded=True):

        st.write(f"**Title:** {meta['video_title']}")
        st.write(f"**Channel:** {meta['channel_title']}")
        st.write(f"**Views:** {meta['view_count']:,}")
        st.write(f"**Risk Level:** {execs['risk_level']}")

        chart = pd.DataFrame({
            "Sentiment": ["Positive","Neutral","Negative"],
            "Value": [
                summary["positive_pct"],
                summary["neutral_pct"],
                summary["negative_pct"]
            ]
        })

        fig = px.pie(
            chart,
            names="Sentiment",
            values="Value",
            hole=0.68
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            margin=dict(l=10,r=10,t=10,b=10)
        )

        st.plotly_chart(
            fig,
            width='stretch',
            config={
                "displayModeBar": False,
                "staticPlot": True,
                "responsive": True
            }
        )

    # COMMENTS
    with st.expander("✦ Comment Intelligence", expanded=True):

        df = pd.DataFrame(data["comments"])[
            ["author","comment","sentiment","likes","language"]
        ].copy()

        df["author"] = df["author"].astype(str)
        df["comment"] = df["comment"].astype(str).str.slice(0,120)
        df["likes"] = pd.to_numeric(
            df["likes"],
            errors="coerce"
        ).fillna(0).astype(int)

        df["language"] = df["language"].astype(str)

        df.columns = [
            "Author",
            "Comment",
            "Sentiment",
            "Likes",
            "Language"
        ]

        def color_sentiment(val):
            v = str(val).lower()

            if v == "positive":
                return """
                background-color: rgba(34,197,94,.18);
                color:#4ade80;
                font-weight:700;
                """

            elif v == "negative":
                return """
                background-color: rgba(239,68,68,.18);
                color:#f87171;
                font-weight:700;
                """

            return """
            background-color: rgba(245,158,11,.18);
            color:#fbbf24;
            font-weight:700;
            """

        styled = (
            df.style
            .map(color_sentiment, subset=["Sentiment"])
            .set_properties(**{
                "background-color":"rgba(255,255,255,.03)",
                "color":"white",
                "border":"1px solid rgba(255,255,255,.06)",
                "font-size":"14px"
            })
            .format({"Likes":"{:,}"})
        )

        st.dataframe(
            styled,
            width='stretch',
            height=520,
            hide_index=True
        )