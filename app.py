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

st.set_page_config(page_title="The Chat Analyst", page_icon="📋", layout="wide", initial_sidebar_state="expanded")

PALETTE = {
    "bg":      "#EDE8DC",
    "surface": "#F5F0E8",
    "border":  "#2A7D6E",
    "accent":  "#2A7D6E",
    "accent2": "#25D366",
    "muted":   "#7AAF9A",
    "text":    "#1A2820",
    "subtext": "#3D6355",
    "rule":    "#B5C9B0",
    "day":     "#25D366",
    "night":   "#2A7D6E",
}

rcParams.update({
    "figure.facecolor": PALETTE["surface"], "axes.facecolor": PALETTE["surface"],
    "axes.edgecolor": PALETTE["border"], "axes.labelcolor": PALETTE["subtext"],
    "xtick.color": PALETTE["subtext"], "ytick.color": PALETTE["subtext"],
    "text.color": PALETTE["text"], "grid.color": PALETTE["rule"],
    "grid.linewidth": 0.5, "axes.grid": True,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": True, "axes.spines.bottom": True,
    "font.family": "serif", "font.size": 10,
})

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Courier+Prime:wght@400;700&display=swap');

html, body, [class*="css"] {{ font-family: 'Courier Prime', monospace; background-color: {PALETTE["bg"]}; color: {PALETTE["text"]}; }}

.main .block-container {{
    background-color: {PALETTE["bg"]};
    background-image: repeating-linear-gradient(0deg, transparent, transparent 27px, {PALETTE["rule"]}55 27px, {PALETTE["rule"]}55 28px);
    padding-top: 2rem; padding-bottom: 4rem; max-width: 1400px;
}}

section[data-testid="stSidebar"] {{ background-color: {PALETTE["accent"]} !important; border-right: 4px double {PALETTE["text"]} !important; }}
section[data-testid="stSidebar"] * {{ color: {PALETTE["surface"]} !important; }}
section[data-testid="stSidebar"] label {{ font-family: 'Courier Prime', monospace !important; font-size: 0.68rem !important; letter-spacing: 0.14em !important; text-transform: uppercase !important; color: {PALETTE["surface"]}BB !important; }}
section[data-testid="stSidebar"] .stSelectbox > div > div, section[data-testid="stSidebar"] .stFileUploader > div {{ background-color: {PALETTE["surface"]}22 !important; border-color: {PALETTE["surface"]}55 !important; border-radius: 0 !important; }}

div[data-testid="metric-container"] {{ background: {PALETTE["surface"]}; border: 2px solid {PALETTE["border"]}; border-radius: 0; padding: 1rem 1.2rem; box-shadow: 4px 4px 0 {PALETTE["border"]}55; }}
div[data-testid="metric-container"] > div:first-child {{ font-family: 'Courier Prime', monospace; font-size: 0.6rem; letter-spacing: 0.18em; text-transform: uppercase; color: {PALETTE["subtext"]}; }}
div[data-testid="metric-container"] > div:nth-child(2) {{ font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: {PALETTE["text"]}; line-height: 1.1; }}

h1 {{ font-family: 'Playfair Display', serif !important; font-size: 1.05rem !important; font-weight: 700 !important; letter-spacing: 0.18em !important; text-transform: uppercase !important; color: {PALETTE["text"]} !important; border-top: 3px double {PALETTE["border"]}; border-bottom: 1px solid {PALETTE["border"]}; padding: 0.4rem 0 !important; margin-top: 2.5rem !important; margin-bottom: 1.2rem !important; }}
h2, h3 {{ font-family: 'Courier Prime', monospace !important; font-size: 0.72rem !important; font-weight: 700 !important; letter-spacing: 0.14em !important; text-transform: uppercase !important; color: {PALETTE["subtext"]} !important; margin-bottom: 0.5rem !important; }}

div[data-testid="stDataFrame"] {{ border: 2px solid {PALETTE["border"]}; border-radius: 0; box-shadow: 4px 4px 0 {PALETTE["border"]}44; }}

div.stButton > button {{ font-family: 'Courier Prime', monospace; font-size: 0.78rem; letter-spacing: 0.18em; text-transform: uppercase; background-color: {PALETTE["text"]}; color: {PALETTE["surface"]}; border: 2px solid {PALETTE["text"]}; border-radius: 0; padding: 0.6rem 1.8rem; width: 100%; box-shadow: 3px 3px 0 {PALETTE["accent2"]}; transition: all 0.15s; }}
div.stButton > button:hover {{ background-color: {PALETTE["accent"]}; border-color: {PALETTE["accent"]}; box-shadow: 4px 4px 0 {PALETTE["accent2"]}; transform: translate(-1px, -1px); }}

.stamp-badge {{ display: inline-block; font-family: 'Courier Prime', monospace; font-size: 0.58rem; letter-spacing: 0.18em; text-transform: uppercase; border: 1.5px solid {PALETTE["surface"]}88; color: {PALETTE["surface"]}CC; padding: 2px 10px; margin-bottom: 0.5rem; }}
.verdict-card {{ background: {PALETTE["surface"]}; border: 2px solid {PALETTE["border"]}; border-left: 6px solid {PALETTE["accent"]}; padding: 0.8rem 1.2rem; font-family: 'Courier Prime', monospace; font-size: 0.88rem; color: {PALETTE["text"]}; margin-bottom: 1rem; box-shadow: 4px 4px 0 {PALETTE["border"]}33; }}
.masthead {{ border-top: 5px double {PALETTE["text"]}; border-bottom: 5px double {PALETTE["text"]}; padding: 0.8rem 0; margin-bottom: 2rem; text-align: center; background: {PALETTE["surface"]}; }}
.masthead-title {{ font-family: 'Playfair Display', serif; font-size: 2.6rem; font-weight: 700; color: {PALETTE["text"]}; letter-spacing: 0.06em; line-height: 1; }}
.masthead-sub {{ font-family: 'Courier Prime', monospace; font-size: 0.62rem; letter-spacing: 0.24em; text-transform: uppercase; color: {PALETTE["subtext"]}; margin-top: 0.25rem; }}
.masthead-rule {{ border: none; border-top: 1px solid {PALETTE["border"]}; margin: 0.4rem 5rem; }}
hr {{ border: none; border-top: 2px double {PALETTE["border"]}; margin: 1rem 0 1.8rem 0; }}
.report-footer {{ text-align: center; font-family: 'Courier Prime', monospace; font-size: 0.62rem; letter-spacing: 0.18em; color: {PALETTE["muted"]}; padding: 0.5rem 0 1rem 0; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def make_fig(h_in=3.4, w_in=None):
    fig, ax = plt.subplots(figsize=(w_in or 6, h_in))
    fig.patch.set_facecolor(PALETTE["surface"])
    ax.set_facecolor(PALETTE["surface"])
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color(PALETTE["border"])
    return fig, ax

with st.sidebar:
    st.markdown(f"""<div style='padding:1rem 0 1.5rem 0; border-bottom:2px double {PALETTE["surface"]}44; margin-bottom:1.5rem;'>
        <div style='font-family:"Playfair Display",serif; font-size:1.4rem; font-weight:700; color:{PALETTE["surface"]}; letter-spacing:0.03em;'>The Chat Analyst</div>
        <div style='font-family:"Courier Prime",monospace; font-size:0.55rem; letter-spacing:0.22em; text-transform:uppercase; color:{PALETTE["surface"]}88; margin-top:0.25rem;'>◆ Intelligence Report ◆</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="stamp-badge">§ I — Data Source</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Export file (.txt)", type=["txt"])
    st.markdown('<div class="stamp-badge">§ II — Format</div>', unsafe_allow_html=True)
    format_type = st.radio("Time format", ["Auto Detect", "12-hour (AM/PM)", "24-hour"], label_visibility="collapsed")
    if uploaded_file:
        st.markdown('<div class="stamp-badge">§ III — Scope</div>', unsafe_allow_html=True)

def detect_format(text):
    sample = "\n".join(text.splitlines()[:10])
    if re.search(r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(AM|PM)', sample, re.IGNORECASE):
        return "12hr"
    return "24hr"

st.markdown(f"""<div class="masthead">
    <hr class="masthead-rule">
    <div class="masthead-title">The Chat Analyst</div>
    <hr class="masthead-rule">
    <div class="masthead-sub">WhatsApp Correspondence Reports &nbsp</div>
</div>""", unsafe_allow_html=True)

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
        selected_usr = st.selectbox("Correspondent", user_list, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("▶  File Report")

    if run:
        # § I
        st.markdown("## § I — Correspondence Summary")
        num_messages, num_words, distinct_words, medias, links = h.fetch_data(selected_usr, df)
        cols = st.columns(5)
        for col, lbl, val in zip(cols, ["Dispatches","Total Words","Distinct Words","Media Sent","Links"], [num_messages, num_words, distinct_words, medias, links]):
            col.metric(lbl, f"{val:,}")
        st.markdown("<hr>", unsafe_allow_html=True)

        # § II
        st.markdown("## § II — Activity Record")
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown("### Monthly Dispatch Volume")
            timeline = h.monthly_timeline(selected_usr, df)
            fig, ax = make_fig(3.4)
            ax.plot(timeline['time'], timeline['message'], color=PALETTE["accent"], linewidth=2, solid_capstyle='round', zorder=3)
            ax.fill_between(timeline['time'], timeline['message'], alpha=0.10, color=PALETTE["accent"])
            ax.scatter(timeline['time'], timeline['message'], color=PALETTE["accent"], s=28, zorder=4)
            ax.set_ylabel("Messages", fontsize=9, labelpad=8)
            plt.xticks(rotation=45, ha='right', fontsize=8)
            fig.tight_layout(pad=1.5)
            st.pyplot(fig)
        with c2:
            st.markdown("### Busiest Day of Week")
            busy_day = h.weekly_activity_map(selected_usr, df)
            fig, ax = make_fig(3.4, w_in=4)
            colors = [PALETTE["accent2"] if i == busy_day.values.argmax() else PALETTE["accent"] for i in range(len(busy_day))]
            ax.barh(busy_day.index, busy_day.values, color=colors, height=0.55, edgecolor=PALETTE["bg"], linewidth=0.8)
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
            ax.set_xlabel("Messages", fontsize=9)
            fig.tight_layout(pad=1.5)
            st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # § III
        if selected_usr == 'overall':
            st.markdown("## § III — Correspondent Breakdown")
            x, new_df = h.fetch_most_busy_users(df)
            c1, c2 = st.columns([2, 3])
            with c1:
                st.markdown("### Message Count by Correspondent")
                fig, ax = make_fig(3.6)
                ax.bar(x.index, x.values, color=PALETTE["accent"], width=0.55, edgecolor=PALETTE["bg"], linewidth=0.8)
                plt.xticks(rotation=45, ha='right', fontsize=8)
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
                fig.tight_layout(pad=1.5)
                st.pyplot(fig)
            with c2:
                st.markdown("### Share of Voice — Percentage Table")
                st.dataframe(new_df.style.background_gradient(cmap="YlGn", subset=new_df.select_dtypes("number").columns).format(precision=1), use_container_width=True, height=260)
            st.markdown("<hr>", unsafe_allow_html=True)

        # § IV
        st.markdown("## § IV — Vocabulary & Lexical Analysis")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Word Cloud")
            df_wc = h.create_wordcloud(selected_usr, df)
            fig, ax = plt.subplots(figsize=(6, 3.4))
            fig.patch.set_facecolor(PALETTE["surface"])
            ax.set_facecolor(PALETTE["surface"])
            ax.imshow(df_wc)
            ax.axis('off')
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(1.5)
                spine.set_color(PALETTE["border"])
            fig.tight_layout(pad=0.5)
            st.pyplot(fig)
        with c2:
            st.markdown("### Top 20 Most Frequent Words")
            new_df_words = h.max_word(selected_usr, df)
            fig, ax = make_fig(4.0)
            n = len(new_df_words)
            bar_colors = [PALETTE["accent2"] if i >= n - 3 else PALETTE["accent"] for i in range(n)]
            ax.barh(new_df_words['word'], new_df_words['count'], color=bar_colors, height=0.62, edgecolor=PALETTE["bg"], linewidth=0.5)
            ax.set_xlabel("Occurrences", fontsize=9)
            ax.invert_yaxis()
            fig.tight_layout(pad=1.5)
            st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # § V
        st.markdown("## § V — Temporal Activity Heatmap")
        st.markdown("### Message Frequency · Day × Hour")
        user_heatmap = h.User_heatmap(selected_usr, df)
        fig, ax = plt.subplots(figsize=(12, 3.0))
        fig.patch.set_facecolor(PALETTE["surface"])
        ax.set_facecolor(PALETTE["surface"])
        cmap = sns.light_palette(PALETTE["accent"], as_cmap=True)
        sns.heatmap(user_heatmap, ax=ax, cmap=cmap, linewidths=0.4, linecolor=PALETTE["bg"], cbar_kws={"shrink": 0.65, "pad": 0.01})
        ax.tick_params(axis='both', labelsize=8)
        plt.xticks(rotation=0)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1.2)
            spine.set_color(PALETTE["border"])
        fig.tight_layout(pad=1.2)
        st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # § VI
        st.markdown("## § VI — Response Latency Analysis")
        avg_response, monthly_trend, fastest, slowest = h.response_time_analysis(selected_usr, df)
        if selected_usr == 'overall':
            c1, c2 = st.columns(2)
            with c1: st.metric("⚡ Fastest Correspondent", fastest)
            with c2: st.metric("🐢 Slowest Correspondent", slowest)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Avg. Response Time per Correspondent (min)")
                fig, ax = make_fig(3.4)
                ax.barh(avg_response.index, avg_response.values, color=PALETTE["accent2"], height=0.55, edgecolor=PALETTE["bg"], linewidth=0.8)
                ax.set_xlabel("Minutes", fontsize=9)
                fig.tight_layout(pad=1.5)
                st.pyplot(fig)
            with c2:
                st.markdown("### Monthly Response Time Trend")
                fig, ax = make_fig(3.4)
                ax.plot(range(len(monthly_trend)), monthly_trend.values, marker='s', markersize=5, linewidth=1.8, color=PALETTE["accent2"], markerfacecolor=PALETTE["surface"], markeredgewidth=1.5)
                ax.fill_between(range(len(monthly_trend)), monthly_trend.values, alpha=0.08, color=PALETTE["accent2"])
                ax.set_xticks(range(len(monthly_trend)))
                ax.set_xticklabels(monthly_trend.index, rotation=45, ha='right', fontsize=8)
                ax.set_ylabel("Avg. Minutes", fontsize=9)
                fig.tight_layout(pad=1.5)
                st.pyplot(fig)
        else:
            st.markdown("### Monthly Response Time Trend")
            fig, ax = make_fig(3.2, w_in=10)
            ax.plot(range(len(monthly_trend)), monthly_trend.values, marker='s', markersize=5, linewidth=1.8, color=PALETTE["accent2"], markerfacecolor=PALETTE["surface"], markeredgewidth=1.5)
            ax.fill_between(range(len(monthly_trend)), monthly_trend.values, alpha=0.08, color=PALETTE["accent2"])
            ax.set_xticks(range(len(monthly_trend)))
            ax.set_xticklabels(monthly_trend.index, rotation=45, ha='right', fontsize=8)
            ax.set_ylabel("Avg. Minutes", fontsize=9)
            fig.tight_layout(pad=1.5)
            st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # § VII
        st.markdown("## § VII — Diurnal Activity Profile")
        result = h.day_night_activity(selected_usr, df)

        if result[0] == 'single':
            _, personality, day_count, night_count, day_pct, night_pct, hourly = result
            st.markdown(f'<div class="verdict-card">◆ &nbsp; Field Verdict: <strong>{personality}</strong></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Day / Night Distribution")
                fig, ax = plt.subplots(figsize=(4, 3.4))
                fig.patch.set_facecolor(PALETTE["surface"])
                ax.set_facecolor(PALETTE["surface"])
                wedges, texts, autotexts = ax.pie([day_count, night_count], labels=['Day', 'Night'], autopct='%1.1f%%', colors=[PALETTE["day"], PALETTE["night"]], startangle=90, wedgeprops={"linewidth": 2.5, "edgecolor": PALETTE["surface"]})
                for t in texts + autotexts:
                    t.set_color(PALETTE["text"])
                    t.set_fontsize(9)
                fig.tight_layout()
                st.pyplot(fig)
            with c2:
                st.markdown("### Hourly Message Distribution")
                fig, ax = make_fig(3.4, w_in=5)
                bar_colors = [PALETTE["day"] if t == 'Day' else PALETTE["night"] for t in hourly['time_of_day']]
                ax.bar(hourly['hour'], hourly['count'], color=bar_colors, width=0.78, edgecolor=PALETTE["bg"], linewidth=0.5)
                ax.set_xlabel("Hour of Day", fontsize=9)
                ax.set_ylabel("Messages", fontsize=9)
                from matplotlib.patches import Patch
                ax.legend(handles=[Patch(facecolor=PALETTE["day"], label='Day', edgecolor=PALETTE["bg"]), Patch(facecolor=PALETTE["night"], label='Night', edgecolor=PALETTE["bg"])], fontsize=8, framealpha=0.4, edgecolor=PALETTE["rule"])
                fig.tight_layout(pad=1.5)
                st.pyplot(fig)
        else:
            _, day_people, night_people = result
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### ☀  Day Correspondents")
                if not day_people.empty:
                    fig, ax = make_fig(3.4)
                    ax.barh(day_people['user'], day_people['day_pct'], color=PALETTE["day"], height=0.55, edgecolor=PALETTE["bg"], linewidth=0.8)
                    ax.set_xlabel("% of Messages During Day", fontsize=9)
                    ax.set_xlim(0, 100)
                    fig.tight_layout(pad=1.5)
                    st.pyplot(fig)
                    st.dataframe(day_people[['user', 'day_pct', 'night_pct']].reset_index(drop=True), use_container_width=True, height=160)
                else:
                    st.info("No day-dominant correspondents found.")
            with c2:
                st.markdown("### ☽  Night Correspondents")
                if not night_people.empty:
                    fig, ax = make_fig(3.4)
                    ax.barh(night_people['user'], night_people['night_pct'], color=PALETTE["night"], height=0.55, edgecolor=PALETTE["bg"], linewidth=0.8)
                    ax.set_xlabel("% of Messages During Night", fontsize=9)
                    ax.set_xlim(0, 100)
                    fig.tight_layout(pad=1.5)
                    st.pyplot(fig)
                    st.dataframe(night_people[['user', 'day_pct', 'night_pct']].reset_index(drop=True), use_container_width=True, height=160)
                else:
                    st.info("No night-dominant correspondents found.")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="report-footer">◆ &nbsp; END OF REPORT &nbsp; ◆</div>', unsafe_allow_html=True)

else:
    st.markdown(f"""<div style='border:3px double {PALETTE["border"]}; padding:3.5rem 2rem; text-align:center; margin-top:1rem; background:{PALETTE["surface"]}; box-shadow:5px 5px 0 {PALETTE["border"]}33;'>
        <div style='font-family:"Playfair Display",serif; font-size:1rem; font-weight:700; letter-spacing:0.22em; color:{PALETTE["subtext"]}; text-transform:uppercase; margin-bottom:0.6rem;'>— Awaiting Dossier —</div>
        <div style='font-family:"Courier Prime",monospace; font-size:0.82rem; color:{PALETTE["text"]}; letter-spacing:0.05em; line-height:1.8;'>Upload a WhatsApp chat export<br>from the sidebar to file your report.</div>
        <div style='font-family:"Courier Prime",monospace; font-size:0.65rem; color:{PALETTE["muted"]}; margin-top:1.2rem; letter-spacing:0.1em;'>WhatsApp &rarr; Chat &rarr; Export Chat &rarr; Without Media</div>
    </div>""", unsafe_allow_html=True)