import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Signal Desk — Resume Screener",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)
#BACKEND_URL = "https://resumescreener-backend-j872.onrender.com/api/screen"

BACKEND_URL = "http://127.0.0.1:8000/api/screen"
# ----------------------------------------------------------------------------
# Design tokens
# ----------------------------------------------------------------------------
BG          = "#0E1116"
PANEL       = "#161B24"
PANEL_EDGE  = "#242B38"
TEXT        = "#EDEFF4"
MUTED       = "#8891A3"
SIGNAL      = "#5EEAD4"   # strong match — teal
SIGNAL_DIM  = "#2E5A54"
MID         = "#F2B84B"   # amber — mid match
LOW         = "#FB7185"   # rose — weak match

def tier_color(score: float) -> str:
    if score >= 75:
        return SIGNAL
    if score >= 50:
        return MID
    return LOW

# ----------------------------------------------------------------------------
# Global styling
# ----------------------------------------------------------------------------
st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">

<style>
.stApp {{
    background: {BG};
    color: {TEXT};
    font-family: 'Inter', sans-serif;
}}
[data-testid="stSidebar"] {{
    background: {PANEL};
    border-right: 1px solid {PANEL_EDGE};
}}
[data-testid="stSidebar"] * {{
    color: {TEXT};
}}
h1, h2, h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.01em;
}}
#MainMenu, footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{
    background: transparent !important;
}}
[data-testid="collapsedControl"] {{
    visibility: visible !important;
    color: {TEXT} !important;
}}
[data-testid="collapsedControl"] svg {{
    fill: {TEXT} !important;
}}

/* Hero */
.desk-hero {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 32px;
    background: linear-gradient(120deg, {PANEL} 0%, #121721 100%);
    border: 1px solid {PANEL_EDGE};
    border-radius: 14px;
    margin-bottom: 28px;
}}
.desk-hero .eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.18em;
    color: {SIGNAL};
    text-transform: uppercase;
    margin-bottom: 6px;
}}
.desk-hero h1 {{
    font-size: 30px;
    margin: 0;
    color: {TEXT};
}}
.desk-hero p {{
    color: {MUTED};
    margin-top: 6px;
    font-size: 14.5px;
    max-width: 560px;
}}
.desk-hero .dot {{
    width: 10px; height: 10px; border-radius: 50%;
    background: {SIGNAL};
    box-shadow: 0 0 12px {SIGNAL};
    display: inline-block;
    margin-right: 8px;
}}

/* Sidebar label styling */
.sidebar-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {SIGNAL};
    margin-bottom: 4px;
    margin-top: 4px;
}}

/* Section headers */
.section-head {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 20px;
    font-weight: 600;
    margin: 6px 0 16px 0;
    color: {TEXT};
    display: flex;
    align-items: baseline;
    gap: 10px;
}}
.section-head .tag {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: {MUTED};
    letter-spacing: 0.1em;
}}

/* Candidate dossier card */
.dossier {{
    background: {PANEL};
    border: 1px solid {PANEL_EDGE};
    border-left: 3px solid var(--tier);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 14px;
}}
.dossier-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
}}
.dossier-name {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 17px;
    font-weight: 600;
    color: {TEXT};
}}
.dossier-rank {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: {MUTED};
    letter-spacing: 0.08em;
}}
.readout {{
    text-align: right;
    min-width: 92px;
}}
.readout .score {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px;
    font-weight: 600;
    color: var(--tier);
    line-height: 1;
}}
.readout .label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: {MUTED};
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}
.meter {{
    height: 5px;
    width: 100%;
    background: {PANEL_EDGE};
    border-radius: 3px;
    margin: 14px 0 12px 0;
    overflow: hidden;
}}
.meter-fill {{
    height: 100%;
    background: var(--tier);
    border-radius: 3px;
}}
.dossier-summary {{
    color: {MUTED};
    font-size: 14px;
    line-height: 1.55;
    margin-bottom: 10px;
}}
.chip {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    color: {TEXT};
    background: #1E2530;
    border: 1px solid {PANEL_EDGE};
    padding: 3px 9px;
    border-radius: 5px;
    margin: 3px 5px 0 0;
}}

/* Text area (job description input) */
[data-testid="stTextArea"] textarea {{
    background: {PANEL} !important;
    color: {TEXT} !important;
    border: 1px solid {PANEL_EDGE} !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stTextArea"] textarea::placeholder {{
    color: {MUTED} !important;
    opacity: 1 !important;
}}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {{
    background: {PANEL} !important;
    border: 1px dashed {PANEL_EDGE} !important;
    border-radius: 8px !important;
}}
[data-testid="stFileUploaderDropzone"] * {{
    color: {TEXT} !important;
}}
[data-testid="stFileUploaderDropzone"] small {{
    color: {MUTED} !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    background: transparent !important;
    color: {TEXT} !important;
    border: 1px solid {PANEL_EDGE} !important;
}}
[data-testid="stFileUploaderDropzone"] button:hover {{
    border-color: {SIGNAL} !important;
    color: {SIGNAL} !important;
}}
/* Uploaded file row */
[data-testid="stFileUploaderFile"] {{
    background: #1E2530 !important;
    color: {TEXT} !important;
    border-radius: 6px !important;
}}
[data-testid="stFileUploaderFile"] * {{
    color: {TEXT} !important;
}}
[data-testid="stFileUploaderFileName"] {{
    color: {TEXT} !important;
}}

/* Buttons */
.stButton>button {{
    background: {SIGNAL};
    color: #06201C;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 10px 0;
    font-family: 'Space Grotesk', sans-serif;
}}
.stButton>button:hover {{
    background: #7EF3E2;
    color: #06201C;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(f"""
<div class="desk-hero">
    <div>
        <div class="eyebrow"><span class="dot"></span>SIGNAL DESK · RESUME SCREENING</div>
        <h1>Screen candidates against the role, not the pile</h1>
        <p>Paste a job description and drop in resumes. The desk reads each one,
        scores its match to the role, and surfaces who's worth a closer look.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Sidebar — intake
# ----------------------------------------------------------------------------
st.sidebar.markdown('<div class="sidebar-label">01 · Role</div>', unsafe_allow_html=True)
job_description = st.sidebar.text_area(
    "Job description",
    height=220,
    placeholder="Paste the full job description here…",
    label_visibility="collapsed",
)

st.sidebar.markdown('<div class="sidebar-label">02 · Candidates</div>', unsafe_allow_html=True)
uploaded_files = st.sidebar.file_uploader(
    "Resumes",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
screen_button = st.sidebar.button("Run the scan →", type="primary", use_container_width=True)

if uploaded_files:
    st.sidebar.markdown(
        f'<div style="font-family:IBM Plex Mono, monospace; font-size:12px; color:{MUTED}; margin-top:10px;">'
        f'{len(uploaded_files)} file(s) queued</div>',
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
if screen_button:
    if not job_description.strip():
        st.error("The desk needs a job description before it can score anything.")
    elif not uploaded_files:
        st.error("Add at least one resume — nothing to compare the role against yet.")
    else:
        with st.spinner("Reading resumes and scoring against the role…"):
            try:
                files = [("resumes", (f.name, f.getvalue(), "application/pdf")) for f in uploaded_files]
                data = {"job_description": job_description}
                response = requests.post(BACKEND_URL, data=data, files=files)

                if response.status_code == 200:
                    result = response.json()
                    candidates = sorted(
                        result.get("candidates", []),
                        key=lambda c: c.get("match_score", 0),
                        reverse=True,
                    )

                    st.markdown(
                        f'<div style="font-family:IBM Plex Mono, monospace; font-size:12.5px; color:{SIGNAL}; '
                        f'margin-bottom:18px;">✓ {len(candidates)} candidate(s) processed</div>',
                        unsafe_allow_html=True,
                    )

                    # ---- Analytics ----
                    st.markdown(
                        '<div class="section-head">Match distribution '
                        f'<span class="tag">SCORE BY CANDIDATE</span></div>',
                        unsafe_allow_html=True,
                    )

                    df = pd.DataFrame(candidates)
                    bar_colors = [tier_color(s) for s in df["match_score"]]

                    fig = go.Figure(
                        go.Bar(
                            x=df["candidate_name"],
                            y=df["match_score"],
                            marker_color=bar_colors,
                            marker_line_width=0,
                            hovertemplate="%{x}<br>Match: %{y}%<extra></extra>",
                        )
                    )
                    fig.update_layout(
                        plot_bgcolor=PANEL,
                        paper_bgcolor=BG,
                        font=dict(color=TEXT, family="Inter"),
                        yaxis=dict(range=[0, 100], gridcolor=PANEL_EDGE, title="Match score (%)"),
                        xaxis=dict(title=None),
                        margin=dict(t=20, l=10, r=10, b=10),
                        height=340,
                        bargap=0.35,
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                    # ---- Ranked dossiers ----
                    st.markdown(
                        '<div class="section-head">Ranked candidates '
                        f'<span class="tag">{len(candidates)} TOTAL</span></div>',
                        unsafe_allow_html=True,
                    )

                    for rank, cand in enumerate(candidates, 1):
                        score = cand.get("match_score", 0)
                        color = tier_color(score)
                        skills = cand.get("matched_skills", [])
                        chips = "".join(f'<span class="chip">{s}</span>' for s in skills)

                        st.markdown(f"""
                        <div class="dossier" style="--tier:{color};">
                            <div class="dossier-top">
                                <div>
                                    <div class="dossier-rank">CANDIDATE {rank:02d}</div>
                                    <div class="dossier-name">{cand.get('candidate_name', 'Unnamed')}</div>
                                </div>
                                <div class="readout">
                                    <div class="score">{score}%</div>
                                    <div class="label">Match</div>
                                </div>
                            </div>
                            <div class="meter"><div class="meter-fill" style="width:{min(score,100)}%;"></div></div>
                            <div class="dossier-summary">{cand.get('summary', '')}</div>
                            {chips}
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    detail = response.json().get("detail", "Failed to process request")
                    st.error(f"Backend error: {detail}")

            except Exception as e:
                st.error(
                    "Could not reach the FastAPI backend. Make sure it's running on "
                    f"http://127.0.0.1:8000 — {e}"
                )
else:
    st.markdown(f"""
    <div style="border:1px dashed {PANEL_EDGE}; border-radius:12px; padding:40px;
                text-align:center; color:{MUTED}; margin-top:10px;">
        <div style="font-family:'Space Grotesk', sans-serif; font-size:17px; color:{TEXT}; margin-bottom:6px;">
            Nothing on the desk yet
        </div>
        Paste a job description and upload resumes in the sidebar, then run the scan.
    </div>
    """, unsafe_allow_html=True)