import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
from matplotlib import rcParams
import seaborn as sns
import preprocessor1 as pp1
import preprocessor2 as pp2
import helper as h
import streamlit as st
import re

# ── Config ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChatLens",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens ──────────────────────────────────────────────────────────────
C = {
    "bg":       "#F7F9F8",
    "surface":  "#FFFFFF",
    "surface2": "#F0F7F4",
    "border":   "#D4E8E0",
    "teal":     "#1A7A5E",
    "green":    "#25D366",
    "green_lt": "#E8F8F0",
    "text":     "#0F1F1A",
    "sub":      "#4A6B5F",
    "muted":    "#8AADA0",
    "divider":  "#E2EDE9",
    "warn":     "#E8A020",
    "warn_lt":  "#FEF3E2",
}

# ── Matplotlib theme ───────────────────────────────────────────────────────────
rcParams.update({
    "figure.facecolor":   C["surface"],
    "axes.facecolor":     C["surface"],
    "axes.edgecolor":     C["border"],
    "axes.labelcolor":    C["sub"],
    "axes.labelsize":     9,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.spines.bottom": True,
    "axes.grid":          True,
    "axes.axisbelow":     True,
    "grid.color":         C["divider"],
    "grid.linewidth":     0.6,
    "xtick.color":        C["muted"],
    "xtick.labelsize":    8,
    "ytick.color":        C["muted"],
    "ytick.labelsize":    8,
    "ytick.left":         False,
    "text.color":         C["text"],
    "font.family":        "sans-serif",
    "font.size":          9,
})

# ── Loader HTML (no auto-hide JS — dismissed by Python via loader_slot.empty())
LOADER = f"""
<div id="cl-loader" style="position:fixed;inset:0;z-index:9999;
  background:{C['bg']};display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:20px;">
<style>
  .cl-logo{{font-size:2rem;font-weight:700;color:{C['teal']};
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            letter-spacing:-0.03em;}}
  .cl-logo span{{color:{C['green']};}}
  .cl-msg{{font-size:0.78rem;color:{C['muted']};
           font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
           letter-spacing:0.02em;min-height:1.2em;}}
  .cl-track{{width:220px;height:3px;background:{C['border']};border-radius:99px;overflow:hidden;}}
  .cl-fill{{height:100%;background:linear-gradient(90deg,{C['teal']},{C['green']});
            border-radius:99px;animation:clBar 2.4s ease-in-out infinite;}}
  @keyframes clBar{{0%{{width:0%}}70%{{width:80%}}90%{{width:88%}}100%{{width:88%}}}}
</style>
<div class="cl-logo">Chat<span>Lens</span></div>
<div class="cl-track"><div class="cl-fill"></div></div>
<div class="cl-msg" id="cl-msg">Preparing analysis…</div>
</div>
<script>
(function(){{
  var msgs=["Parsing messages…","Computing timelines…","Analysing vocabulary…",
            "Mapping activity…","Calculating response times…","Building insights…",
            "Almost ready…"];
  var i=0,el=document.getElementById('cl-msg');
  if(el)setInterval(function(){{el.textContent=msgs[i=(i+1)%msgs.length];}},1400);
}})();
</script>
"""

# ── CSS only — no loader injected at page load ─────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html,body,[class*="css"]{{
  font-family:'Inter',system-ui,sans-serif;
  background:{C['bg']}; color:{C['text']};
}}

.main .block-container{{
  background:{C['bg']};
  padding:1.5rem 2rem 4rem;
  max-width:1360px;
}}

section[data-testid="stSidebar"]{{
  background:{C['surface']} !important;
  border-right:1px solid {C['divider']} !important;
}}
section[data-testid="stSidebar"] *{{color:{C['text']} !important;}}
section[data-testid="stSidebar"] label{{
  font-size:0.7rem !important;
  font-weight:600 !important;
  letter-spacing:0.06em !important;
  text-transform:uppercase !important;
  color:{C['muted']} !important;
}}
section[data-testid="stSidebar"] .stSelectbox>div>div,
section[data-testid="stSidebar"] .stFileUploader>div{{
  border-radius:8px !important;
  border-color:{C['border']} !important;
  background:{C['bg']} !important;
}}

div[data-testid="metric-container"]{{
  background:{C['surface']};
  border:1px solid {C['divider']};
  border-radius:12px;
  padding:1.1rem 1.3rem;
  transition:box-shadow .2s;
}}
div[data-testid="metric-container"]:hover{{
  box-shadow:0 4px 16px {C['teal']}18;
}}
div[data-testid="metric-container"]>div:first-child{{
  font-size:0.67rem; font-weight:600;
  letter-spacing:0.08em; text-transform:uppercase;
  color:{C['muted']};
}}
div[data-testid="metric-container"]>div:nth-child(2){{
  font-size:1.85rem; font-weight:700;
  color:{C['text']}; line-height:1.15; margin-top:2px;
}}

h1{{
  font-size:0.7rem !important; font-weight:700 !important;
  letter-spacing:0.1em !important; text-transform:uppercase !important;
  color:{C['muted']} !important;
  margin:2.5rem 0 1rem !important; padding:0 !important;
  border:none !important;
}}
h2,h3{{
  font-size:0.75rem !important; font-weight:600 !important;
  letter-spacing:0.05em !important; text-transform:uppercase !important;
  color:{C['sub']} !important; margin-bottom:0.5rem !important;
}}

.chart-card{{
  background:{C['surface']};
  border:1px solid {C['divider']};
  border-radius:12px;
  padding:1.2rem 1.4rem 1rem;
}}

.insight{{
  background:{C['surface2']};
  border-left:3px solid {C['teal']};
  border-radius:0 8px 8px 0;
  padding:0.65rem 1rem;
  font-size:0.82rem; color:{C['sub']};
  margin:0.5rem 0 1rem;
  line-height:1.55;
}}
.insight strong{{color:{C['teal']};}}

.verdict{{
  display:inline-flex; align-items:center; gap:8px;
  background:{C['green_lt']}; border:1px solid {C['green']}44;
  border-radius:8px; padding:0.55rem 1rem;
  font-size:0.82rem; font-weight:500; color:{C['teal']};
  margin-bottom:1rem;
}}

.tag{{
  display:inline-block;
  background:{C['surface2']}; border:1px solid {C['border']};
  border-radius:99px; padding:2px 10px;
  font-size:0.68rem; font-weight:600;
  color:{C['sub']}; margin:2px;
}}
.tag-green{{background:{C['green_lt']};border-color:{C['green']}55;color:{C['teal']};}}
.tag-warn{{background:{C['warn_lt']};border-color:{C['warn']}55;color:{C['warn']};}}

hr{{border:none;border-top:1px solid {C['divider']};margin:1.6rem 0;}}

div[data-testid="stDataFrame"]{{
  border:1px solid {C['divider']};
  border-radius:10px; overflow:hidden;
}}

div.stButton>button{{
  font-size:0.8rem; font-weight:600;
  letter-spacing:0.04em;
  background:{C['teal']}; color:#fff;
  border:none; border-radius:8px;
  padding:0.6rem 1.4rem; width:100%;
  transition:background .15s,transform .1s;
}}
div.stButton>button:hover{{
  background:{C['green']}; transform:translateY(-1px);
}}

.footer{{
  text-align:center;
  font-size:0.7rem; color:{C['muted']};
  padding:1.5rem 0 0.5rem;
  letter-spacing:0.04em;
}}

.empty-state{{
  text-align:center;
  padding:5rem 2rem;
  background:{C['surface']};
  border:1px dashed {C['border']};
  border-radius:16px;
  margin-top:1rem;
}}
.empty-icon{{font-size:2.4rem;margin-bottom:1rem;}}
.empty-title{{font-size:1.1rem;font-weight:600;color:{C['sub']};margin-bottom:0.4rem;}}
.empty-desc{{font-size:0.82rem;color:{C['muted']};line-height:1.7;}}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def card(fig):
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)
    plt.close(fig)

def make_fig(h=3.2, w=None):
    fig, ax = plt.subplots(figsize=(w or 5.5, h))
    fig.patch.set_facecolor(C["surface"])
    ax.set_facecolor(C["surface"])
    return fig, ax

def bar_colors(n, highlight_last=3):
    return [C["green"] if i >= n - highlight_last else C["teal"] for i in range(n)]

def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)

def section(label):
    st.markdown(f"## {label}")

def detect_format(text):
    sample = "\n".join(text.splitlines()[:10])
    return "12hr" if re.search(
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(AM|PM)', sample, re.IGNORECASE
    ) else "24hr"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:1.2rem 0 1.4rem;
                border-bottom:1px solid {C['divider']};
                margin-bottom:1.4rem;">
      <div style="font-size:1.35rem;font-weight:700;color:{C['teal']};
                  font-family:'Inter',sans-serif;letter-spacing:-0.02em;">
        Chat<span style="color:{C['green']}">Lens</span>
      </div>
      <div style="font-size:0.68rem;color:{C['muted']};
                  margin-top:0.2rem;letter-spacing:0.04em;">
        WhatsApp Conversation Intelligence
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.7rem;font-weight:600;letter-spacing:0.06em;'
                f'text-transform:uppercase;color:{C["muted"]};margin-bottom:4px;">Upload Export</p>',
                unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["txt"], label_visibility="collapsed")

    st.markdown('<p style="font-size:0.7rem;font-weight:600;letter-spacing:0.06em;'
                f'text-transform:uppercase;color:{C["muted"]};margin:12px 0 4px;">Time Format</p>',
                unsafe_allow_html=True)
    format_type = st.radio(
        "", ["Auto Detect", "12-hour (AM/PM)", "24-hour"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.markdown('<p style="font-size:0.7rem;font-weight:600;letter-spacing:0.06em;'
                    f'text-transform:uppercase;color:{C["muted"]};margin:12px 0 4px;">View</p>',
                    unsafe_allow_html=True)


# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:flex-end;justify-content:space-between;
            border-bottom:1px solid {C['divider']};padding-bottom:1rem;margin-bottom:0.5rem;">
  <div>
    <div style="font-size:1.5rem;font-weight:700;color:{C['teal']};
                letter-spacing:-0.02em;">
      Chat<span style="color:{C['green']}">Lens</span>
    </div>
    <div style="font-size:0.78rem;color:{C['muted']};margin-top:2px;">
      WhatsApp Conversation Intelligence
    </div>
  </div>
  <div style="font-size:0.68rem;color:{C['muted']};">
    Upload an export · Select a view · Run analysis
  </div>
</div>
""", unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────
if uploaded_file is None:
    st.markdown(f"""
    <div class="empty-state">
      <div class="empty-icon">💬</div>
      <div class="empty-title">No conversation loaded</div>
      <div class="empty-desc">
        Upload a WhatsApp export from the sidebar to begin.<br>
        <span style="color:{C['teal']};font-weight:500;">
          WhatsApp → Chat → ⋮ → Export Chat → Without Media
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Parse ──────────────────────────────────────────────────────────────────────
raw = uploaded_file.getvalue().decode("utf-8")
if format_type == "Auto Detect":
    df = pp2.preprocess(raw) if re.search(r'\d{1,2}:\d{2}\s?(AM|PM)', raw) else pp1.preprocess(raw)
elif format_type == "12-hour (AM/PM)":
    df = pp2.preprocess(raw)
else:
    df = pp1.preprocess(raw)

user_list = [u for u in df["user"].unique().tolist() if u != "group_notification"]
user_list.sort()
user_list.insert(0, "overall")

with st.sidebar:
    selected = st.selectbox("", user_list, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("Run Analysis →")

if not run:
    st.markdown(f"""
    <div class="empty-state">
      <div class="empty-icon">✅</div>
      <div class="empty-title">File loaded — ready to analyse</div>
      <div class="empty-desc">
        Choose a participant in the sidebar, then hit <strong>Run Analysis</strong>.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Show loader, run all computation, then dismiss loader ──────────────────────
# The loader is injected as a Streamlit placeholder. Python controls when it
# disappears by calling loader_slot.empty() — no JS timers or browser events
# are involved, so it stays visible for exactly as long as computation takes.
loader_slot = st.empty()
loader_slot.markdown(LOADER, unsafe_allow_html=True)

total_msgs, total_words, distinct_words, total_media, total_links = h.fetch_data(selected, df)
timeline      = h.monthly_timeline(selected, df)
busy_day      = h.weekly_activity_map(selected, df)
wc            = h.create_wordcloud(selected, df)
top_words     = h.max_word(selected, df)
heatmap_data  = h.User_heatmap(selected, df)
avg_resp, monthly_resp, fastest, slowest = h.response_time_analysis(selected, df)
day_night     = h.day_night_activity(selected, df)

if selected == "overall":
    top_users, users_pct = h.fetch_most_busy_users(df)

# ── Dismiss loader — all data is ready, Streamlit will now render results ──────
loader_slot.empty()

# ══════════════════════════════════════════════════════════════════════════════
# 1 · OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
section("Overview")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Messages",      f"{total_msgs:,}")
c2.metric("Words",         f"{total_words:,}")
c3.metric("Unique Words",  f"{distinct_words:,}")
c4.metric("Media Shared",  f"{total_media:,}")
c5.metric("Links Shared",  f"{total_links:,}")

avg_words_per_msg = round(total_words / total_msgs, 1) if total_msgs else 0
vocab_richness    = round(distinct_words / total_words * 100, 1) if total_words else 0
insight(
    f"On average each message contains <strong>{avg_words_per_msg} words</strong>. "
    f"<strong>{vocab_richness}%</strong> of all words are unique, "
    f"indicating {'a rich and varied' if vocab_richness > 30 else 'a fairly repetitive'} vocabulary."
)

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 2 · ACTIVITY PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
section("Activity Patterns")
c1, c2 = st.columns([3, 2], gap="medium")

with c1:
    st.markdown("### Message volume over time")
    fig, ax = make_fig(3.0, w=7)
    ax.plot(timeline["time"], timeline["message"],
            color=C["teal"], linewidth=1.8, zorder=3, solid_capstyle="round")
    ax.fill_between(timeline["time"], timeline["message"],
                    alpha=0.08, color=C["teal"])
    ax.scatter(timeline["time"], timeline["message"],
               color=C["teal"], s=22, zorder=4)
    peak_idx = timeline["message"].idxmax()
    ax.annotate(
        f"Peak: {timeline['message'][peak_idx]:,}",
        xy=(timeline["time"][peak_idx], timeline["message"][peak_idx]),
        xytext=(8, 8), textcoords="offset points",
        fontsize=7.5, color=C["teal"], fontweight="600",
    )
    ax.set_ylabel("Messages", fontsize=8, labelpad=6)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    plt.xticks(rotation=40, ha="right", fontsize=7.5)
    fig.tight_layout(pad=1.2)
    card(fig)

with c2:
    st.markdown("### Day of week breakdown")
    fig, ax = make_fig(3.0, w=4.2)
    colors = [C["green"] if i == busy_day.values.argmax() else C["teal"]
              for i in range(len(busy_day))]
    bars = ax.barh(busy_day.index, busy_day.values,
                   color=colors, height=0.55, edgecolor="none")
    for bar, val in zip(bars, busy_day.values):
        ax.text(val + busy_day.values.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{int(val):,}", va="center", ha="left", fontsize=7, color=C["sub"])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_xlabel("Messages", fontsize=8)
    ax.grid(axis="y", visible=False)
    fig.tight_layout(pad=1.2)
    card(fig)

peak_month = timeline.loc[timeline["message"].idxmax(), "time"]
peak_day   = busy_day.idxmax()
insight(
    f"Activity peaked in <strong>{peak_month}</strong>. "
    f"<strong>{peak_day}</strong> is consistently the busiest day of the week, "
    f"while <strong>{busy_day.idxmin()}</strong> sees the least activity."
)

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3 · WHO TALKS MOST (overall only)
# ══════════════════════════════════════════════════════════════════════════════
if selected == "overall":
    section("Participant Breakdown")
    c1, c2 = st.columns([2, 3], gap="medium")

    with c1:
        st.markdown("### Messages per participant")
        fig, ax = make_fig(max(2.8, len(top_users) * 0.38), w=4.5)
        pal = [C["green"] if i == 0 else C["teal"] for i in range(len(top_users))]
        bars = ax.bar(top_users.index, top_users.values,
                      color=pal, width=0.55, edgecolor="none")
        for bar, val in zip(bars, top_users.values):
            ax.text(bar.get_x() + bar.get_width() / 2, val + top_users.values.max() * 0.01,
                    f"{int(val):,}", ha="center", va="bottom", fontsize=7, color=C["sub"])
        plt.xticks(rotation=35, ha="right", fontsize=7.5)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
        ax.grid(axis="x", visible=False)
        fig.tight_layout(pad=1.2)
        card(fig)

    with c2:
        st.markdown("### Share of voice")
        st.dataframe(
            users_pct.style
                .background_gradient(cmap="YlGn",
                                     subset=users_pct.select_dtypes("number").columns)
                .format(precision=1),
            use_container_width=True,
            height=min(300, 38 + len(users_pct) * 35),
        )

    top_sender  = top_users.idxmax()
    top_pct_raw = top_users.max() / top_users.sum() * 100
    insight(
        f"<strong>{top_sender}</strong> dominates the conversation, "
        f"contributing <strong>{top_pct_raw:.1f}%</strong> of all messages. "
        f"The chat has <strong>{len(top_users)}</strong> active participants."
    )

    st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 4 · VOCABULARY
# ══════════════════════════════════════════════════════════════════════════════
section("Vocabulary Analysis")
c1, c2 = st.columns(2, gap="medium")

with c1:
    st.markdown("### Word cloud")
    fig, ax = plt.subplots(figsize=(6, 3.2))
    fig.patch.set_facecolor(C["surface"])
    ax.set_facecolor(C["surface"])
    ax.imshow(wc)
    ax.axis("off")
    fig.tight_layout(pad=0.3)
    card(fig)

with c2:
    st.markdown("### Top 20 words")
    fig, ax = make_fig(3.8, w=5)
    n = len(top_words)
    bc = [C["green"] if i < 3 else C["teal"] for i in range(n)]
    ax.barh(top_words["word"], top_words["count"],
            color=bc, height=0.65, edgecolor="none")
    ax.set_xlabel("Occurrences", fontsize=8)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    fig.tight_layout(pad=1.2)
    card(fig)

top3 = ", ".join([f"<strong>{w}</strong>" for w in top_words["word"].head(3).tolist()])
insight(f"The three most frequent words are {top3}. "
        f"The vocabulary spans <strong>{distinct_words:,} unique words</strong> "
        f"across <strong>{total_words:,}</strong> total words.")

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 5 · HOURLY HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
section("When People Chat")
st.markdown("### Message density — day of week × hour")

fig, ax = plt.subplots(figsize=(13, 2.8))
fig.patch.set_facecolor(C["surface"])
ax.set_facecolor(C["surface"])
cmap = sns.light_palette(C["teal"], as_cmap=True)
sns.heatmap(
    heatmap_data, ax=ax, cmap=cmap,
    linewidths=0.3, linecolor=C["bg"],
    cbar_kws={"shrink": 0.6, "pad": 0.015, "label": "messages"},
)
ax.tick_params(axis="both", labelsize=7.5)
ax.set_xlabel("")
ax.set_ylabel("")
plt.xticks(rotation=0)
for spine in ax.spines.values():
    spine.set_visible(False)
fig.tight_layout(pad=1.0)
card(fig)

hm_flat  = heatmap_data.stack()
hot_day, hot_hour   = hm_flat.idxmax()
cold_day, cold_hour = hm_flat.idxmin()
insight(
    f"The conversation is hottest on <strong>{hot_day} around {hot_hour}:00</strong>. "
    f"Messages are scarcest on <strong>{cold_day} at {cold_hour}:00</strong>. "
    f"Use the heatmap to spot recurring quiet periods or social rituals."
)

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 6 · RESPONSE DYNAMICS
# ══════════════════════════════════════════════════════════════════════════════
section("Response Dynamics")

if selected == "overall":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⚡ Fastest Responder", fastest)
    c2.metric("🐢 Slowest Responder", slowest)
    if fastest in avg_resp.index:
        c3.metric("Fastest avg (min)", f"{avg_resp[fastest]:.1f}")
    if slowest in avg_resp.index:
        c4.metric("Slowest avg (min)", f"{avg_resp[slowest]:.1f}")

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown("### Avg. response time by participant (min)")
        fig, ax = make_fig(max(2.8, len(avg_resp) * 0.4), w=5)
        resp_colors = [C["warn"] if v == avg_resp.max() else
                       C["green"] if v == avg_resp.min() else C["teal"]
                       for v in avg_resp.values]
        bars = ax.barh(avg_resp.index, avg_resp.values,
                       color=resp_colors, height=0.55, edgecolor="none")
        for bar, val in zip(bars, avg_resp.values):
            ax.text(val + avg_resp.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}m", va="center", ha="left", fontsize=7, color=C["sub"])
        ax.set_xlabel("Minutes", fontsize=8)
        ax.grid(axis="y", visible=False)
        fig.tight_layout(pad=1.2)
        card(fig)

    with c2:
        st.markdown("### Response time trend over months")
        fig, ax = make_fig(2.8, w=5)
        ax.plot(range(len(monthly_resp)), monthly_resp.values,
                color=C["teal"], linewidth=1.8,
                marker="o", markersize=4,
                markerfacecolor=C["surface"], markeredgewidth=1.5,
                markeredgecolor=C["teal"])
        ax.fill_between(range(len(monthly_resp)), monthly_resp.values,
                        alpha=0.07, color=C["teal"])
        ax.set_xticks(range(len(monthly_resp)))
        ax.set_xticklabels(monthly_resp.index, rotation=40, ha="right", fontsize=7.5)
        ax.set_ylabel("Avg minutes", fontsize=8)
        fig.tight_layout(pad=1.2)
        card(fig)

    gap = avg_resp.max() - avg_resp.min()
    insight(
        f"<strong>{fastest}</strong> replies fastest (avg {avg_resp.min():.1f} min). "
        f"<strong>{slowest}</strong> takes the longest (avg {avg_resp.max():.1f} min) — "
        f"a <strong>{gap:.1f}-minute gap</strong> between the quickest and slowest responders."
    )
else:
    st.markdown("### Your response time over months")
    fig, ax = make_fig(2.8, w=11)
    ax.plot(range(len(monthly_resp)), monthly_resp.values,
            color=C["teal"], linewidth=1.8,
            marker="o", markersize=4,
            markerfacecolor=C["surface"], markeredgewidth=1.5,
            markeredgecolor=C["teal"])
    ax.fill_between(range(len(monthly_resp)), monthly_resp.values,
                    alpha=0.07, color=C["teal"])
    ax.set_xticks(range(len(monthly_resp)))
    ax.set_xticklabels(monthly_resp.index, rotation=40, ha="right", fontsize=7.5)
    ax.set_ylabel("Avg minutes", fontsize=8)
    fig.tight_layout(pad=1.2)
    card(fig)
    insight(
        f"Average response time across the entire period: "
        f"<strong>{monthly_resp.mean():.1f} min</strong>. "
        f"Best month: <strong>{monthly_resp.idxmin()}</strong> "
        f"({monthly_resp.min():.1f} min)."
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 7 · DAY vs NIGHT
# ══════════════════════════════════════════════════════════════════════════════
section("Day vs Night Profile")

if day_night[0] == "single":
    _, personality, day_count, night_count, day_pct, night_pct, hourly = day_night

    is_night = night_pct > day_pct
    st.markdown(
        f'<div class="verdict">'
        f'{"🌙" if is_night else "☀️"} &nbsp;'
        f'<strong>{personality}</strong> — '
        f'{"Night owl" if is_night else "Day person"}: '
        f'{night_pct:.1f}% night messages vs {day_pct:.1f}% day'
        f'</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown("### Day vs night split")
        fig, ax = plt.subplots(figsize=(4, 3.2))
        fig.patch.set_facecolor(C["surface"])
        ax.set_facecolor(C["surface"])
        wedges, texts, autotexts = ax.pie(
            [day_count, night_count],
            labels=["Day", "Night"],
            autopct="%1.1f%%",
            colors=[C["green"], C["teal"]],
            startangle=90,
            wedgeprops={"linewidth": 2.5, "edgecolor": C["surface"]},
        )
        for t in texts + autotexts:
            t.set_fontsize(8.5)
            t.set_color(C["text"])
        fig.tight_layout()
        card(fig)

    with c2:
        st.markdown("### Messages by hour")
        fig, ax = make_fig(3.2, w=5.2)
        h_colors = [C["green"] if t == "Day" else C["teal"]
                    for t in hourly["time_of_day"]]
        ax.bar(hourly["hour"], hourly["count"],
               color=h_colors, width=0.78, edgecolor="none", alpha=0.9)
        ax.set_xlabel("Hour", fontsize=8)
        ax.set_ylabel("Messages", fontsize=8)
        ax.legend(
            handles=[
                mpatches.Patch(color=C["green"], label="Day (6–22h)"),
                mpatches.Patch(color=C["teal"],  label="Night (22–6h)"),
            ],
            fontsize=7.5, framealpha=0, edgecolor="none",
        )
        peak_h = hourly.loc[hourly["count"].idxmax(), "hour"]
        ax.axvline(peak_h, color=C["muted"], linewidth=0.8, linestyle="--")
        ax.text(peak_h + 0.3, hourly["count"].max() * 0.95,
                f"Peak: {peak_h}h", fontsize=7, color=C["sub"])
        fig.tight_layout(pad=1.2)
        card(fig)

    peak_hour = hourly.loc[hourly["count"].idxmax(), "hour"]
    insight(
        f"Most messages are sent around <strong>{peak_hour}:00</strong>. "
        f"Overall this is a <strong>{'night-dominant' if is_night else 'day-dominant'}</strong> chat — "
        f"{night_pct:.1f}% of messages are sent between 22:00 and 06:00."
    )

else:
    _, day_people, night_people = day_night
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        st.markdown("### ☀ Day people")
        if not day_people.empty:
            fig, ax = make_fig(max(2.4, len(day_people) * 0.38), w=4.5)
            ax.barh(day_people["user"], day_people["day_pct"],
                    color=C["green"], height=0.55, edgecolor="none")
            ax.set_xlabel("% messages during day", fontsize=8)
            ax.set_xlim(0, 100)
            ax.grid(axis="y", visible=False)
            fig.tight_layout(pad=1.2)
            card(fig)
        else:
            st.info("No strongly day-dominant users found.")

    with c2:
        st.markdown("### 🌙 Night owls")
        if not night_people.empty:
            fig, ax = make_fig(max(2.4, len(night_people) * 0.38), w=4.5)
            ax.barh(night_people["user"], night_people["night_pct"],
                    color=C["teal"], height=0.55, edgecolor="none")
            ax.set_xlabel("% messages during night", fontsize=8)
            ax.set_xlim(0, 100)
            ax.grid(axis="y", visible=False)
            fig.tight_layout(pad=1.2)
            card(fig)
        else:
            st.info("No strongly night-dominant users found.")

    dp  = len(day_people)  if not day_people.empty  else 0
    np_ = len(night_people) if not night_people.empty else 0
    insight(
        f"Of the active participants, <strong>{dp}</strong> are primarily day texters "
        f"and <strong>{np_}</strong> are night owls. "
        f"Scheduling group conversations around the overlap will get faster responses."
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    f'<div class="footer">ChatLens · WhatsApp Conversation Intelligence · '
    f'{total_msgs:,} messages analysed</div>',
    unsafe_allow_html=True,
)