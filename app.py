import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import rcParams
import seaborn as sns
import preprocessor1 as pp1
import preprocessor2 as pp2
import helper as h
import streamlit as st
import re

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat Analytics",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global theme ───────────────────────────────────────────────────────────────
PALETTE = {
    "bg":        "#EDE8E0",        # warm cream — swatch 4
    "surface":   "#F7F5F0",        # lighter cream for cards/panels
    "border":    "#C8E6C9",        # soft mint border
    "accent":    "#2A7D6E",        # deep teal — swatch 1
    "accent2":   "#25D366",        # bright WhatsApp green — swatch 2
    "muted":     "#7AAF9A",        # muted teal
    "text":      "#1A3028",        # dark green — primary text
    "subtext":   "#4E7A68",        # medium teal — secondary text
    "day":       "#25D366",        # bright green for day
    "night":     "#2A7D6E",        # deep teal for night
}

rcParams.update({
    "figure.facecolor":  PALETTE["surface"],
    "axes.facecolor":    PALETTE["surface"],
    "axes.edgecolor":    PALETTE["border"],
    "axes.labelcolor":   PALETTE["subtext"],
    "xtick.color":       PALETTE["subtext"],
    "ytick.color":       PALETTE["subtext"],
    "text.color":        PALETTE["text"],
    "grid.color":        PALETTE["border"],
    "grid.linewidth":    0.6,
    "axes.grid":         True,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.family":       "monospace",
    "font.size":         10,
})

# ── CSS injection ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: {PALETTE["bg"]};
    color: {PALETTE["text"]};
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: {PALETTE["surface"]} !important;
    border-right: 1px solid {PALETTE["border"]} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {PALETTE["text"]} !important;
}}
section[data-testid="stSidebar"] .stFileUploader label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: {PALETTE["muted"]} !important;
}}

/* Main background */
.main .block-container {{
    background-color: {PALETTE["bg"]};
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1400px;
}}

/* Metric cards */
div[data-testid="metric-container"] {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 6px;
    padding: 1rem 1.2rem;
    transition: border-color 0.2s;
}}
div[data-testid="metric-container"]:hover {{
    border-color: {PALETTE["accent"]};
}}
div[data-testid="metric-container"] > div:first-child {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {PALETTE["muted"]};
}}
div[data-testid="metric-container"] > div:nth-child(2) {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: {PALETTE["text"]};
}}

/* Section headers */
h1 {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {PALETTE["accent"]} !important;
    border-bottom: 1px solid {PALETTE["border"]};
    padding-bottom: 0.5rem;
    margin-top: 2.5rem !important;
    margin-bottom: 1.2rem !important;
}}
h2, h3 {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: {PALETTE["subtext"]} !important;
    margin-bottom: 0.6rem !important;
}}

/* Dataframe */
div[data-testid="stDataFrame"] {{
    border: 1px solid {PALETTE["border"]};
    border-radius: 6px;
    overflow: hidden;
}}

/* Button */
div.stButton > button {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background-color: {PALETTE["accent"]};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.55rem 1.6rem;
    width: 100%;
    transition: background-color 0.2s, transform 0.1s;
}}
div.stButton > button:hover {{
    background-color: {PALETTE["accent2"]};
    transform: translateY(-1px);
}}

/* Pill badge */
.badge {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: {PALETTE["border"]};
    color: {PALETTE["subtext"]};
    border-radius: 3px;
    padding: 2px 8px;
    margin-bottom: 0.3rem;
}}
.verdict-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-left: 3px solid {PALETTE["accent"]};
    border-radius: 6px;
    padding: 0.9rem 1.2rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9rem;
    color: {PALETTE["text"]};
    margin-bottom: 1rem;
}}
.page-title {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: {PALETTE["text"]};
    letter-spacing: 0.06em;
    margin-bottom: 0;
}}
.page-sub {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.82rem;
    color: {PALETTE["muted"]};
    margin-top: 0.2rem;
    margin-bottom: 2rem;
}}
hr {{
    border: none;
    border-top: 1px solid {PALETTE["border"]};
    margin: 0.5rem 0 1.5rem 0;
}}
</style>
""", unsafe_allow_html=True)

# ── Helper: styled figure ──────────────────────────────────────────────────────
def make_fig(h_in=3.4, w_in=None):
    fig, ax = plt.subplots(figsize=(w_in or 6, h_in))
    fig.patch.set_alpha(0)
    ax.set_facecolor(PALETTE["surface"])
    return fig, ax

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
        <span style='font-family:"IBM Plex Mono",monospace; font-size:1.1rem; font-weight:600; color:#1A3028'>
            <span style='color:#25D366'>●</span> Chat Analytics
        </span><br>
        <span style='font-family:"IBM Plex Mono",monospace; font-size:0.65rem; letter-spacing:0.1em; color:#7AAF9A; text-transform:uppercase'>
            WhatsApp · Analysis Suite
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="badge">01 · Upload</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Export file (.txt)", type=["txt"])

    st.markdown('<p class="badge">02 · Format</p>', unsafe_allow_html=True)
    format_type = st.radio(
        "Time format",
        ["Auto Detect", "12-hour (AM/PM)", "24-hour"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.markdown('<p class="badge">03 · Scope</p>', unsafe_allow_html=True)


def detect_format(text):
    sample = "\n".join(text.splitlines()[:10])
    if re.search(r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(AM|PM)', sample, re.IGNORECASE):
        return "12hr"
    return "24hr"

# ── Main page title ────────────────────────────────────────────────────────────
st.markdown('<p class="page-title">Chat Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Upload a WhatsApp export to begin analysis</p>', unsafe_allow_html=True)

# ── Main logic ────────────────────────────────────────────────────────────────
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    if format_type == "Auto Detect":
        df = pp2.preprocess(data) if re.search(r'\d{1,2}:\d{2}\s?(AM|PM)', data) else pp1.preprocess(data)
    elif format_type == "12-hour (AM/PM)":
        df = pp2.preprocess(data)
    else:
        df = pp1.preprocess(data)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, 'overall')

    with st.sidebar:
        selected_usr = st.selectbox("Participant", user_list, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("Run Analysis →")

    if run:

        # ── 1 · Summary metrics ────────────────────────────────────────────────
        st.markdown("## — Overview")
        num_messages, num_words, distinct_words, medias, links = h.fetch_data(selected_usr, df)

        cols = st.columns(5)
        labels = ["Messages", "Words", "Distinct Words", "Media", "Links"]
        values = [num_messages, num_words, distinct_words, medias, links]
        for col, lbl, val in zip(cols, labels, values):
            col.metric(lbl, f"{val:,}")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── 2 · Timeline + Activity map ────────────────────────────────────────
        st.markdown("## — Activity Patterns")
        c1, c2 = st.columns([3, 2])

        with c1:
            st.markdown("### Monthly Message Volume")
            timeline = h.monthly_timeline(selected_usr, df)
            fig, ax = make_fig(3.2)
            ax.plot(timeline['time'], timeline['message'],
                    color=PALETTE["accent"], linewidth=1.8, zorder=3)
            ax.fill_between(timeline['time'], timeline['message'],
                            alpha=0.12, color=PALETTE["accent"])
            ax.set_xlabel("")
            ax.set_ylabel("Messages", fontsize=9)
            plt.xticks(rotation=45, ha='right', fontsize=8)
            fig.tight_layout()
            st.pyplot(fig)

        with c2:
            st.markdown("### Day of Week")
            busy_day = h.weekly_activity_map(selected_usr, df)
            fig, ax = make_fig(3.2, w_in=4)
            bars = ax.barh(busy_day.index, busy_day.values,
                           color=PALETTE["accent"], alpha=0.85, height=0.6)
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
            ax.set_xlabel("Messages", fontsize=9)
            # highlight max
            max_idx = busy_day.values.argmax()
            bars[max_idx].set_color(PALETTE["accent2"])
            fig.tight_layout()
            st.pyplot(fig)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── 3 · User activity (overall only) ──────────────────────────────────
        if selected_usr == 'overall':
            st.markdown("## — Participant Breakdown")
            x, new_df = h.fetch_most_busy_users(df)
            c1, c2 = st.columns([2, 3])

            with c1:
                st.markdown("### Message Share")
                fig, ax = make_fig(3.4)
                ax.bar(x.index, x.values, color=PALETTE["accent"], alpha=0.85, width=0.55)
                plt.xticks(rotation=45, ha='right', fontsize=8)
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
                fig.tight_layout()
                st.pyplot(fig)

            with c2:
                st.markdown("### Percentage Table")
                st.dataframe(
                    new_df.style
                        .background_gradient(cmap="Blues", subset=new_df.select_dtypes("number").columns)
                        .format(precision=1),
                    use_container_width=True,
                    height=260,
                )

            st.markdown("<hr>", unsafe_allow_html=True)

        # ── 4 · Word analysis ─────────────────────────────────────────────────
        st.markdown("## — Vocabulary Analysis")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Word Cloud")
            df_wc = h.create_wordcloud(selected_usr, df)
            fig, ax = plt.subplots(figsize=(6, 3.2))
            fig.patch.set_alpha(0)
            ax.set_facecolor(PALETTE["surface"])
            ax.imshow(df_wc)
            ax.axis('off')
            fig.tight_layout(pad=0)
            st.pyplot(fig)

        with c2:
            st.markdown("### Top 20 Words")
            new_df = h.max_word(selected_usr, df)
            fig, ax = make_fig(3.8)
            bars = ax.barh(new_df['word'], new_df['count'],
                           color=PALETTE["accent"], alpha=0.85, height=0.65)
            # gradient color by rank
            n = len(bars)
            for i, bar in enumerate(bars):
                bar.set_alpha(0.4 + 0.6 * (i / max(n - 1, 1)))
            ax.set_xlabel("Count", fontsize=9)
            ax.invert_yaxis()
            fig.tight_layout()
            st.pyplot(fig)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── 5 · Heatmap ────────────────────────────────────────────────────────
        st.markdown("## — Hourly Heatmap")
        st.markdown("### Messages by day × hour")
        user_heatmap = h.User_heatmap(selected_usr, df)
        fig, ax = plt.subplots(figsize=(12, 2.8))
        fig.patch.set_alpha(0)
        ax.set_facecolor(PALETTE["surface"])
        sns.heatmap(
            user_heatmap, ax=ax,
            cmap="BuGn",
            linewidths=0.3, linecolor=PALETTE["bg"],
            cbar_kws={"shrink": 0.7, "pad": 0.01},
        )
        ax.tick_params(axis='both', labelsize=8)
        plt.xticks(rotation=0)
        fig.tight_layout()
        st.pyplot(fig)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── 6 · Response time ─────────────────────────────────────────────────
        st.markdown("## — Response Dynamics")
        avg_response, monthly_trend, fastest, slowest = h.response_time_analysis(selected_usr, df)

        if selected_usr == 'overall':
            c1, c2 = st.columns(2)
            with c1:
                st.metric("⚡ Fastest Responder", fastest)
            with c2:
                st.metric("🐢 Slowest Responder", slowest)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Avg Response Time / User (min)")
                fig, ax = make_fig(3.4)
                ax.barh(avg_response.index, avg_response.values,
                        color=PALETTE["accent2"], alpha=0.85, height=0.6)
                ax.set_xlabel("Minutes", fontsize=9)
                fig.tight_layout()
                st.pyplot(fig)

            with c2:
                st.markdown("### Response Time Trend")
                fig, ax = make_fig(3.4)
                ax.plot(monthly_trend.index, monthly_trend.values,
                        marker='o', markersize=5, linewidth=1.8,
                        color=PALETTE["accent2"])
                ax.fill_between(range(len(monthly_trend)), monthly_trend.values,
                                alpha=0.1, color=PALETTE["accent2"])
                ax.set_xticks(range(len(monthly_trend)))
                ax.set_xticklabels(monthly_trend.index, rotation=45, ha='right', fontsize=8)
                ax.set_ylabel("Avg Minutes", fontsize=9)
                fig.tight_layout()
                st.pyplot(fig)
        else:
            st.markdown("### Response Time Trend")
            fig, ax = make_fig(3.2, w_in=10)
            ax.plot(monthly_trend.index, monthly_trend.values,
                    marker='o', markersize=5, linewidth=1.8,
                    color=PALETTE["accent2"])
            ax.fill_between(range(len(monthly_trend)), monthly_trend.values,
                            alpha=0.1, color=PALETTE["accent2"])
            ax.set_xticks(range(len(monthly_trend)))
            ax.set_xticklabels(monthly_trend.index, rotation=45, ha='right', fontsize=8)
            ax.set_ylabel("Avg Minutes", fontsize=9)
            fig.tight_layout()
            st.pyplot(fig)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── 7 · Day / Night ────────────────────────────────────────────────────
        st.markdown("## — Day vs Night Profile")
        result = h.day_night_activity(selected_usr, df)

        if result[0] == 'single':
            _, personality, day_count, night_count, day_pct, night_pct, hourly = result

            st.markdown(f'<div class="verdict-card">🔍 Verdict: <strong>{personality}</strong></div>',
                        unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Day / Night Split")
                fig, ax = plt.subplots(figsize=(4, 3.2))
                fig.patch.set_alpha(0)
                ax.set_facecolor(PALETTE["surface"])
                wedges, texts, autotexts = ax.pie(
                    [day_count, night_count],
                    labels=['Day', 'Night'],
                    autopct='%1.1f%%',
                    colors=[PALETTE["day"], PALETTE["night"]],
                    startangle=90,
                    wedgeprops={"linewidth": 2, "edgecolor": PALETTE["bg"]},
                )
                for t in texts + autotexts:
                    t.set_color(PALETTE["text"])
                    t.set_fontsize(9)
                fig.tight_layout()
                st.pyplot(fig)

            with c2:
                st.markdown("### Hourly Breakdown")
                fig, ax = make_fig(3.2, w_in=5)
                colors = [PALETTE["day"] if t == 'Day' else PALETTE["night"]
                          for t in hourly['time_of_day']]
                ax.bar(hourly['hour'], hourly['count'], color=colors,
                       width=0.8, alpha=0.9)
                ax.set_xlabel("Hour", fontsize=9)
                ax.set_ylabel("Messages", fontsize=9)
                from matplotlib.patches import Patch
                ax.legend(handles=[
                    Patch(facecolor=PALETTE["day"], label='Day'),
                    Patch(facecolor=PALETTE["night"], label='Night'),
                ], fontsize=8, framealpha=0.1)
                fig.tight_layout()
                st.pyplot(fig)

        else:
            _, day_people, night_people = result
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("### ☀️ Day People")
                if not day_people.empty:
                    fig, ax = make_fig(3.4)
                    ax.barh(day_people['user'], day_people['day_pct'],
                            color=PALETTE["day"], alpha=0.85, height=0.6)
                    ax.set_xlabel("% Day Messages", fontsize=9)
                    ax.set_xlim(0, 100)
                    fig.tight_layout()
                    st.pyplot(fig)
                    st.dataframe(
                        day_people[['user', 'day_pct', 'night_pct']].reset_index(drop=True),
                        use_container_width=True,
                        height=160,
                    )
                else:
                    st.info("No day-dominant users found.")

            with c2:
                st.markdown("### 🌙 Night Owls")
                if not night_people.empty:
                    fig, ax = make_fig(3.4)
                    ax.barh(night_people['user'], night_people['night_pct'],
                            color=PALETTE["night"], alpha=0.85, height=0.6)
                    ax.set_xlabel("% Night Messages", fontsize=9)
                    ax.set_xlim(0, 100)
                    fig.tight_layout()
                    st.pyplot(fig)
                    st.dataframe(
                        night_people[['user', 'day_pct', 'night_pct']].reset_index(drop=True),
                        use_container_width=True,
                        height=160,
                    )
                else:
                    st.info("No night-dominant users found.")

else:
    # ── Empty state ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='
        border: 1px dashed #C8E6C9;
        border-radius: 8px;
        padding: 3rem 2rem;
        text-align: center;
        margin-top: 2rem;
        background: #F7F5F0;
    '>
        <div style='font-size:2.5rem; margin-bottom:1rem'>💬</div>
        <div style='font-family:"IBM Plex Mono",monospace; font-size:0.85rem; color:#4E7A68; letter-spacing:0.08em'>
            Upload a WhatsApp chat export<br>from the sidebar to begin
        </div>
        <div style='font-family:"IBM Plex Mono",monospace; font-size:0.65rem; color:#7AAF9A; margin-top:1rem; letter-spacing:0.06em'>
            WhatsApp → Chat → Export Chat → Without Media
        </div>
    </div>
    """, unsafe_allow_html=True)