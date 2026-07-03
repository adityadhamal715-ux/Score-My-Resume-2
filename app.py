"""
app.py — ScoreMyResume v2.1
Dark Glassmorphism UI · 24 Target Roles · 4-Signal ATS · Bug Fixed & Production Ready
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils import (
    extract_text_from_pdf, parse_resume, extract_skills, get_missing_skills,
    calculate_ats_score, predict_job_role, detect_experience_level,
    analyze_projects, analyze_certifications,
    get_learning_recommendations, calculate_resume_score, generate_pdf_report,
    validate_pdf_file,
)

ALL_ROLES = [
    "AI Engineer","Data Scientist","ML Engineer","NLP Engineer",
    "Computer Vision Engineer","Generative AI Engineer",
    "Data Analyst","Data Engineer","Business Analyst","BI Developer",
    "Python Developer","Full Stack Developer","Frontend Developer",
    "Backend Developer","Java Developer","DevOps Engineer",
    "Site Reliability Engineer","Cloud Architect",
    "Android Developer","iOS Developer","Flutter Developer",
    "Cybersecurity Analyst","UI/UX Designer","Blockchain Developer",
]

st.set_page_config(
    page_title="ScoreMyResume — AI-Powered ATS Analyzer",
    page_icon="🎯", layout="wide", initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,html,body,.stApp{font-family:'Inter',sans-serif!important;}

/* ── Dark background ── */
.stApp{
    background:linear-gradient(135deg,#070b14 0%,#0b1628 45%,#081220 75%,#050a12 100%);
    background-attachment:fixed; color:#e2e8f0;
}
.main .block-container{padding:1.2rem 2rem 3rem;max-width:1300px;}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#060c1a 0%,#0b1527 100%)!important;
    border-right:1px solid rgba(59,130,246,0.12)!important;
}
section[data-testid="stSidebar"] *{color:#64748b!important;}
section[data-testid="stSidebar"] .stDivider{border-color:rgba(255,255,255,0.05)!important;}
section[data-testid="stSidebar"] .stSelectbox>div>div{
    background:rgba(255,255,255,0.04)!important;
    border:1px solid rgba(59,130,246,0.2)!important;
    border-radius:8px!important; color:#e2e8f0!important;
}

/* ── Hero ── */
.hero{
    position:relative; overflow:hidden;
    background:linear-gradient(135deg,
        rgba(29,78,216,0.35) 0%,
        rgba(59,130,246,0.2) 45%,
        rgba(124,58,237,0.18) 100%);
    border:1px solid rgba(59,130,246,0.22);
    border-radius:20px; padding:2.5rem 3rem; margin-bottom:1.8rem;
    backdrop-filter:blur(20px);
    box-shadow:0 8px 40px rgba(37,99,235,0.18),inset 0 1px 0 rgba(255,255,255,0.05);
}
.hero::after{
    content:'';position:absolute;top:-40%;right:-8%;
    width:420px;height:420px;
    background:radial-gradient(circle,rgba(99,102,241,0.1) 0%,transparent 65%);
    border-radius:50%;pointer-events:none;
}
.hero-badge{
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.28);
    border-radius:20px;padding:4px 14px;font-size:.7rem;font-weight:600;
    color:#60a5fa;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:.9rem;
}
.hero-title{
    font-size:2.3rem;font-weight:900;letter-spacing:-1px;margin:0 0 .5rem;
    background:linear-gradient(135deg,#ffffff 0%,#93c5fd 60%,#a78bfa 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero-sub{font-size:.9rem;color:#64748b;margin:0;line-height:1.75;}
.hero-stats{display:flex;gap:2.5rem;margin-top:1.6rem;flex-wrap:wrap;}
.hs-num{font-size:1.6rem;font-weight:900;color:#60a5fa;text-shadow:0 0 20px rgba(96,165,250,0.4);}
.hs-lbl{font-size:.68rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.9px;margin-top:2px;font-weight:600;}

/* ── Glass card ── */
.glass{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:16px; padding:1.4rem 1.5rem;
    backdrop-filter:blur(12px); margin-bottom:1rem;
    box-shadow:0 4px 24px rgba(0,0,0,0.25);
    transition:border-color .2s,box-shadow .2s;
}
.glass:hover{border-color:rgba(59,130,246,0.22);box-shadow:0 4px 24px rgba(59,130,246,0.1);}

/* ── Metric tiles ── */
.tiles{display:flex;gap:10px;flex-wrap:wrap;margin:1.2rem 0 1.6rem;}
.tile{
    flex:1;min-width:115px;
    background:rgba(255,255,255,0.035);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:14px;padding:1.1rem .8rem;text-align:center;
    backdrop-filter:blur(10px);position:relative;overflow:hidden;
    transition:transform .15s,border-color .2s;
}
.tile:hover{transform:translateY(-3px);border-color:rgba(59,130,246,0.3);}
.tile::before{
    content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:var(--tc);border-radius:14px 14px 0 0;
}
.tile .v{font-size:1.65rem;font-weight:800;color:var(--tc);line-height:1;}
.tile .l{font-size:.6rem;color:#334155;margin-top:5px;text-transform:uppercase;letter-spacing:.9px;font-weight:500;}

/* ── Section heading ── */
.sh{
    font-size:.67rem;font-weight:700;text-transform:uppercase;
    letter-spacing:1.4px;color:#3b82f6;
    margin:1.1rem 0 .65rem;display:flex;align-items:center;gap:8px;
}
.sh::after{content:'';flex:1;height:1px;background:rgba(255,255,255,0.05);}

/* ── Pills ── */
.pill{display:inline-block;border-radius:20px;padding:3px 12px;font-size:.72rem;font-weight:500;margin:2px;}
.pg{background:rgba(34,197,94,.09);color:#4ade80;border:1px solid rgba(34,197,94,.2);}
.pr{background:rgba(239,68,68,.09);color:#f87171;border:1px solid rgba(239,68,68,.2);}
.pb{background:rgba(59,130,246,.09);color:#60a5fa;border:1px solid rgba(59,130,246,.2);}
.py{background:rgba(234,179,8,.09);color:#facc15;border:1px solid rgba(234,179,8,.2);}

/* ── ATS banner ── */
.ats-banner{
    border-radius:16px;padding:1.5rem 2rem;
    display:flex;align-items:center;gap:2rem;
    margin-bottom:1.2rem;backdrop-filter:blur(10px);border:1px solid;
}
.ats-num{font-size:3.8rem;font-weight:900;line-height:1;}
.ats-grade{font-size:1.1rem;font-weight:700;}
.ats-hint{font-size:.73rem;opacity:.55;margin-top:4px;}

/* ── Signal bars ── */
.sig{margin:8px 0;}
.sig-row{display:flex;justify-content:space-between;font-size:.79rem;font-weight:500;color:#cbd5e1;margin-bottom:4px;}
.sig-bg{background:rgba(255,255,255,0.06);border-radius:6px;height:8px;overflow:hidden;}
.sig-fill{height:100%;border-radius:6px;}
.sig-tip{font-size:.66rem;color:#334155;margin-top:2px;}

/* ── Info rows ── */
.ir{display:flex;gap:.5rem;padding:.45rem 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:.84rem;}
.ik{font-weight:600;color:#334155;min-width:120px;}
.iv{color:#cbd5e1;}

/* ── Feedback ── */
.fb-i{background:rgba(59,130,246,.08);border-left:3px solid #3b82f6;border-radius:8px;padding:.65rem 1rem;margin:.35rem 0;color:#93c5fd;font-size:.82rem;}

/* ── Role bars ── */
.rb{margin:8px 0;}
.rb-row{display:flex;justify-content:space-between;font-size:.81rem;font-weight:500;margin-bottom:4px;}
.rb-bg{background:rgba(255,255,255,0.06);border-radius:6px;height:9px;}
.rb-fill{height:100%;border-radius:6px;}

/* ── Upload ── */
[data-testid="stFileUploader"]{
    background:rgba(15,23,42,0.6)!important;
    border:1px dashed rgba(59,130,246,0.4)!important;
    border-radius:14px!important;
    transition:border-color .2s, box-shadow .2s!important;
    padding:0.5rem!important;
}
[data-testid="stFileUploader"]:hover{
    border-color:rgba(99,102,241,0.7)!important;
    box-shadow:0 0 18px rgba(59,130,246,0.12)!important;
}
[data-testid="stFileUploader"] section{
    display:flex!important;
    flex-direction:column!important;
    align-items:center!important;
    padding:.75rem .5rem!important;
    overflow:hidden!important;
}
[data-testid="stFileUploaderDropzone"]{
    display:flex!important;
    flex-direction:column!important;
    align-items:center!important;
    text-align:center!important;
    overflow:hidden!important;
}
[data-testid="stFileUploaderDropzone"] > div{
    display:flex!important;
    flex-direction:column!important;
    align-items:center!important;
    gap:4px!important;
    overflow:hidden!important;
    white-space:normal!important;
    word-break:break-word!important;
    font-size:.75rem!important;
}
[data-testid="stFileUploaderDropzone"] small{
    font-size:.68rem!important;
    color:#475569!important;
    text-align:center!important;
    display:block!important;
}
[data-testid="stFileUploaderDropzone"] button{
    background:linear-gradient(135deg,rgba(29,78,216,0.3),rgba(99,102,241,0.3))!important;
    border:1px solid rgba(59,130,246,0.4)!important;
    border-radius:8px!important;
    color:#93c5fd!important;
    font-size:.75rem!important;
    font-weight:600!important;
    padding:4px 14px!important;
    margin-top:4px!important;
}

/* ── Upload card shell ── */
.upload-card{
    background:rgba(10,18,35,0.7);
    border:1px solid rgba(59,130,246,0.14);
    border-radius:16px;
    padding:1.2rem 1rem 1rem;
    backdrop-filter:blur(16px);
    box-shadow:0 4px 24px rgba(0,0,0,0.3),inset 0 1px 0 rgba(255,255,255,0.03);
    transition:border-color .2s;
    height:100%;
}
.upload-card:hover{border-color:rgba(59,130,246,0.28);}

/* ── Note banner ── */
.note-banner{
    background:linear-gradient(135deg,rgba(234,179,8,.07),rgba(251,146,60,.06));
    border:1px solid rgba(234,179,8,.22);
    border-radius:12px;
    padding:.7rem 1.1rem;
    display:flex;
    align-items:center;
    gap:.7rem;
    font-size:.79rem;
    color:#fbbf24;
    margin-bottom:1.2rem;
    backdrop-filter:blur(8px);
}
.note-banner strong{color:#fde68a;font-weight:700;}

/* ── Tabs ── */
button[data-baseweb="tab"]{color:#334155!important;font-size:.81rem!important;font-weight:500!important;}
button[data-baseweb="tab"][aria-selected="true"]{
    color:#60a5fa!important;
    background:rgba(59,130,246,0.08)!important;
    border-bottom:2px solid #3b82f6!important;
}

/* ── Buttons ── */
.stButton>button{
    border-radius:10px!important;font-weight:700!important;font-size:.84rem!important;
    border:1px solid rgba(59,130,246,.35)!important;
    background:linear-gradient(135deg,#1d4ed8,#2563eb)!important;
    color:white!important;box-shadow:0 4px 14px rgba(37,99,235,.28)!important;
}
.stButton>button:hover{box-shadow:0 6px 20px rgba(37,99,235,.45)!important;transform:translateY(-1px)!important;}

/* ── Selectbox ── */
.stSelectbox>div>div{
    background:rgba(255,255,255,0.04)!important;
    border:1px solid rgba(59,130,246,0.2)!important;
    border-radius:10px!important; color:#e2e8f0!important;
}

/* ── Textarea / input ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea{
    background:rgba(255,255,255,0.04)!important;
    border:1px solid rgba(255,255,255,0.08)!important;
    border-radius:10px!important; color:#e2e8f0!important;
    font-size:.84rem!important;
}

/* ── Expander ── */
details{background:rgba(255,255,255,0.02)!important;border:1px solid rgba(255,255,255,0.06)!important;border-radius:10px!important;}
summary{color:#475569!important;}

/* ── Alerts ── */
div[data-testid="stAlert"]{border-radius:10px!important;}

/* ══════════════════════════════════════════════════════════════════════
   RESPONSIVE LAYER — mobile & tablet adjustments only.
   No colors, gradients, fonts, borders, animations, or component styles
   are changed above; these rules only adjust sizing/spacing/wrapping so
   nothing clips, overlaps, or forces horizontal scroll on small screens.
   ══════════════════════════════════════════════════════════════════════ */

/* Belt-and-braces: never allow sideways scrolling regardless of viewport */
html, body, .stApp { overflow-x: hidden !important; max-width: 100vw; }
.main .block-container{ overflow-x: hidden; }

/* Make every image / chart / iframe / plotly figure fluid */
img, svg, canvas, .stPlotlyChart, .js-plotly-plot, iframe {
    max-width: 100% !important;
    height: auto;
}
.stPlotlyChart, .js-plotly-plot { width: 100% !important; }

/* Ensure Streamlit's own column layout stacks on small screens
   (Streamlit already does this by default via its own breakpoints;
   this reinforces it without altering desktop column widths) */
@media (max-width: 640px){
    div[data-testid="column"]{ width:100% !important; flex:1 1 100% !important; min-width:100% !important; }
}

/* Tables / dataframes stay within viewport and scroll internally, not the page */
[data-testid="stTable"], [data-testid="stDataFrame"]{
    max-width:100% !important;
    overflow-x:auto !important;
    -webkit-overflow-scrolling:touch;
}

/* Long unbroken strings (emails, urls, filenames) wrap instead of clipping */
.iv, .ik, .ir, .glass, .fb-i, .pill, .sig-row, .rb-row, .hero-sub, .hero-title {
    word-break: break-word;
    overflow-wrap: anywhere;
}

/* Tablet range */
@media (max-width: 992px){
    .main .block-container{ padding:1rem 1.2rem 2rem; }
    .hero{ padding:2rem 1.6rem; }
    .hero-title{ font-size:1.9rem; }
    .hero-stats{ gap:1.6rem; }
    .tiles{ gap:8px; }
    .tile{ min-width:100px; }
}

/* Mobile phones */
@media (max-width: 640px){
    .main .block-container{ padding:.8rem .8rem 2rem; max-width:100%; }

    /* Hero */
    .hero{ padding:1.4rem 1.1rem; border-radius:16px; margin-bottom:1.2rem; }
    .hero-title{ font-size:1.5rem; }
    .hero-sub{ font-size:.82rem; max-width:100%; }
    .hero-badge{ font-size:.62rem; padding:3px 10px; }
    .hero-stats{ gap:1rem 1.4rem; }
    .hs-num{ font-size:1.3rem; }
    .hs-lbl{ font-size:.6rem; }
    .hero > div:first-child{ flex-direction:column; align-items:flex-start!important; gap:8px; }

    /* Metric tiles stack two-per-row instead of clipping */
    .tiles{ gap:8px; }
    .tile{ min-width: calc(50% - 8px); flex: 1 1 calc(50% - 8px); }
    .tile .v{ font-size:1.35rem; }

    /* Glass cards / upload cards get tighter padding */
    .glass{ padding:1.1rem 1rem; }
    .upload-card{ padding:1rem .8rem .8rem; margin-bottom:.8rem; }

    /* Note banner stacks icon above text and wraps cleanly */
    .note-banner{ flex-direction:column; align-items:flex-start; gap:.4rem; padding:.8rem 1rem; }

    /* Section headings wrap gracefully */
    .sh{ font-size:.63rem; flex-wrap:wrap; }

    /* ATS banner: stack number + text instead of a tight row */
    .ats-banner{ flex-direction:column; align-items:flex-start; gap:.6rem; padding:1.2rem 1.3rem; }
    .ats-num{ font-size:2.8rem; }

    /* Info rows wrap instead of forcing a fixed key column */
    .ir{ flex-wrap:wrap; }
    .ik{ min-width:0; flex:1 1 100%; }
    .iv{ flex:1 1 100%; }

    /* Pills wrap naturally (already inline-block) but shrink slightly */
    .pill{ font-size:.68rem; padding:3px 10px; }

    /* Tabs: allow horizontal scroll within the tab bar itself only,
       so the page body never scrolls sideways */
    div[data-baseweb="tab-list"]{
        overflow-x:auto !important;
        overflow-y:hidden;
        flex-wrap:nowrap !important;
        -webkit-overflow-scrolling:touch;
    }
    button[data-baseweb="tab"]{ font-size:.74rem!important; padding:.5rem .6rem!important; white-space:nowrap; }

    /* File uploader shrinks its own text/icons rather than overflowing */
    [data-testid="stFileUploaderDropzone"]{ padding:.4rem!important; }
    [data-testid="stFileUploaderDropzone"] > div{ font-size:.68rem!important; }
    [data-testid="stFileUploaderDropzone"] button{ font-size:.68rem!important; padding:4px 10px!important; }

    /* Buttons full-width and comfortably tappable */
    .stButton>button{ font-size:.8rem!important; padding:.55rem .8rem!important; width:100% !important; }
    [data-testid="stDownloadButton"]>button{ width:100% !important; }
    a[data-testid="stLinkButton"]{ width:100% !important; }

    /* Sidebar content doesn't overflow narrow drawers */
    section[data-testid="stSidebar"]{ min-width: 0 !important; }
}

/* Very small phones */
@media (max-width: 380px){
    .hero-title{ font-size:1.3rem; }
    .ats-num{ font-size:2.2rem; }
    .tile{ min-width: 100%; flex: 1 1 100%; }
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.5rem 0 .8rem'>
        <div style='font-size:3rem;filter:drop-shadow(0 0 14px rgba(59,130,246,.5))'>🎯</div>
        <div style='font-size:1rem;font-weight:800;margin-top:8px;
                    background:linear-gradient(135deg,#60a5fa,#818cf8);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text'>ScoreMyResume</div>
        <div style='font-size:.68rem;color:#1e293b;margin-top:3px'>v2.1 · Production Ready</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div style='font-size:.76rem;color:#334155;line-height:1.85'>
    <div style='color:#3b82f6;font-weight:700;font-size:.68rem;text-transform:uppercase;
                letter-spacing:1.1px;margin-bottom:7px'>Features</div>
    📄 Smart PDF Parsing<br>
    🎯 4-Signal ATS Score<br>
    🔮 24 Role Predictions<br>
    📊 Plotly Visual Analytics<br>
    📥 PDF Report Download<br>
    📚 50+ Course Recommendations<br><br>
    <div style='color:#3b82f6;font-weight:700;font-size:.68rem;text-transform:uppercase;
                letter-spacing:1.1px;margin-bottom:7px'>ATS Signals</div>
    🛠 Skill Gap · 30%<br>
    🔑 JD Keywords · 30%<br>
    🎯 Domain Match · 25%<br>
    📊 Achievements · 15%<br><br>
    <div style='color:#3b82f6;font-weight:700;font-size:.68rem;text-transform:uppercase;
                letter-spacing:1.1px;margin-bottom:7px'>Roles Covered</div>
    AI/ML · Data · Web/Mobile<br>
    DevOps · Cloud · Security<br>
    Design · Blockchain & More
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='font-size:.64rem;color:#0f172a;text-align:center'>Built for AI Engineer portfolio</div>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">

  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:1.1rem;">
    <div class="hero-badge">🎯 AI-Powered Resume Intelligence</div>
    <div style="display:flex;align-items:center;gap:6px;
                background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.22);
                border-radius:20px;padding:4px 12px;">
      <span style="width:7px;height:7px;border-radius:50%;background:#22c55e;
                   display:inline-block;box-shadow:0 0 6px rgba(34,197,94,0.6);
                   animation:pulse-dot 2s infinite;"></span>
      <span style="font-size:.65rem;font-weight:600;color:#4ade80;
                   text-transform:uppercase;letter-spacing:1px;">Live Analysis</span>
    </div>
  </div>

  <div class="hero-title">ScoreMyResume</div>

  <div style="font-size:.88rem;color:#475569;line-height:1.8;margin:.3rem 0 1.4rem;max-width:640px;">
    Upload your resume &amp; job description — get your real
    <span style="color:#93c5fd;font-weight:600;">ATS score</span>,
    <span style="color:#a78bfa;font-weight:600;">skill gap analysis</span>,
    <span style="color:#34d399;font-weight:600;">role prediction</span> &amp;
    <span style="color:#fb923c;font-weight:600;">career recommendations</span>.
  </div>

  <div style="height:1px;background:linear-gradient(90deg,rgba(59,130,246,0.3),rgba(124,58,237,0.15),transparent);margin-bottom:1.3rem;"></div>

  <div class="hero-stats">
    <div style="display:flex;flex-direction:column;gap:2px;min-width:80px;">
      <div class="hs-num">24</div>
      <div class="hs-lbl">Target Roles</div>
      <div style="height:2px;width:28px;background:linear-gradient(90deg,#3b82f6,#818cf8);border-radius:2px;margin-top:4px;"></div>
    </div>
    <div style="width:1px;background:rgba(255,255,255,0.05);align-self:stretch;"></div>
    <div style="display:flex;flex-direction:column;gap:2px;min-width:80px;">
      <div class="hs-num">150+</div>
      <div class="hs-lbl">Skills Tracked</div>
      <div style="height:2px;width:28px;background:linear-gradient(90deg,#818cf8,#a78bfa);border-radius:2px;margin-top:4px;"></div>
    </div>
    <div style="width:1px;background:rgba(255,255,255,0.05);align-self:stretch;"></div>
    <div style="display:flex;flex-direction:column;gap:2px;min-width:80px;">
      <div class="hs-num">4</div>
      <div class="hs-lbl">ATS Signals</div>
      <div style="height:2px;width:28px;background:linear-gradient(90deg,#22c55e,#34d399);border-radius:2px;margin-top:4px;"></div>
    </div>
    <div style="width:1px;background:rgba(255,255,255,0.05);align-self:stretch;"></div>
    <div style="display:flex;flex-direction:column;gap:2px;min-width:80px;">
      <div class="hs-num">50+</div>
      <div class="hs-lbl">Courses Mapped</div>
      <div style="height:2px;width:28px;background:linear-gradient(90deg,#fb923c,#f59e0b);border-radius:2px;margin-top:4px;"></div>
    </div>
  </div>

</div>

<style>
@keyframes pulse-dot {
  0%,100%{opacity:1;transform:scale(1);}
  50%{opacity:.5;transform:scale(1.4);}
}
</style>
""", unsafe_allow_html=True)

# ── Tip note ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="note-banner">
  <span style="font-size:1.2rem">📌</span>
  <div>
    Note: Upload your Resume PDF in both the Resume PDF and Job Description PDF sections to receive the complete analysis and accurate output.
  </div>
</div>""", unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 2, 1.2])

with c1:
    st.markdown("""
    <div class="upload-card">
      <div class="sh">📄 Resume PDF</div>
      <div style="font-size:.71rem;color:#334155;margin-bottom:.6rem;line-height:1.6">
        Upload your resume · <span style="color:#60a5fa">PDF format only</span><br>
        <span style="color:#1e3a5f">Skills · Experience · Projects extracted automatically</span>
      </div>
    </div>""", unsafe_allow_html=True)
    resume_file = st.file_uploader("resume", type=["pdf"], label_visibility="collapsed")

with c2:
    st.markdown("""
    <div class="upload-card">
      <div class="sh">📋 Job Description PDF <span style="color:#334155;font-size:.65rem;text-transform:none;letter-spacing:0">(optional)</span></div>
      <div style="font-size:.71rem;color:#334155;margin-bottom:.6rem;line-height:1.6">
        Upload the JD PDF · enables full ATS signal breakdown
      </div>
    </div>""", unsafe_allow_html=True)
    jd_file = st.file_uploader("jd_pdf", type=["pdf"], label_visibility="collapsed")

with c3:
    st.markdown('<div class="sh">🎯 Target Role</div>', unsafe_allow_html=True)
    target_role = st.selectbox("role", label_visibility="collapsed", options=ALL_ROLES)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    run = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)
    st.markdown("""
    <div style="font-size:.67rem;color:#1e3a5f;text-align:center;margin-top:6px;line-height:1.6">
      🔒 Runs locally<br>Your data stays private
    </div>""", unsafe_allow_html=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
if run:
    if not resume_file:
        st.error("⚠️ Please upload a resume PDF first.")
        st.stop()

    # Validate PDF file
    validation_error = validate_pdf_file(resume_file)
    if validation_error:
        st.error(f"❌ {validation_error}")
        st.stop()

    with st.spinner("📖 Extracting text from PDF…"):
        rtext = extract_text_from_pdf(resume_file)
        if rtext.startswith("ERROR:") or len(rtext) < 50:
            st.error(f"❌ Could not extract text from resume. Ensure it contains readable text (not a scanned image). Error: {rtext}")
            st.stop()

    jd_text = ""
    if jd_file:
        jd_validation = validate_pdf_file(jd_file)
        if jd_validation:
            st.warning(f"⚠️ Job description could not be validated: {jd_validation}")
        else:
            jd_text = extract_text_from_pdf(jd_file)
            if jd_text.startswith("ERROR:") or len(jd_text) < 30:
                st.warning("⚠️ Job description could not be parsed. ATS score will be limited.")
                jd_text = ""

    with st.spinner("🧠 Running AI analysis…"):
        parsed  = parse_resume(rtext)
        fskills = extract_skills(rtext)
        mskills = get_missing_skills(fskills, target_role)
        ats     = calculate_ats_score(rtext, jd_text)
        rpred   = predict_job_role(rtext)
        explvl  = detect_experience_level(rtext, parsed)
        projA   = analyze_projects(rtext)
        certA   = analyze_certifications(rtext)
        rscore  = calculate_resume_score(parsed, fskills, projA, certA, ats)
        recs    = get_learning_recommendations(mskills)

    st.success("✅ Analysis complete!")

    # ── Metric tiles ──────────────────────────────────────────────────
    def tc(v, hi=70, lo=45):
        return "#22c55e" if v >= hi else ("#f59e0b" if v >= lo else "#ef4444")

    sc = rscore["total"]; at = ats["ats_score"]
    st.markdown(f"""
    <div class="tiles">
      <div class="tile" style="--tc:{tc(sc)}">
        <div class="v">{sc}</div><div class="l">Resume Score</div></div>
      <div class="tile" style="--tc:{tc(at)}">
        <div class="v">{at}%</div><div class="l">ATS Score</div></div>
      <div class="tile" style="--tc:#818cf8">
        <div class="v" style="font-size:1rem;padding-top:.5rem;color:#818cf8">
          {rpred['top_role'].split()[0]}</div>
        <div class="l">Top Role</div></div>
      <div class="tile" style="--tc:#38bdf8">
        <div class="v" style="font-size:1rem;padding-top:.5rem;color:#38bdf8">
          {explvl['level']}</div>
        <div class="l">Experience</div></div>
      <div class="tile" style="--tc:#fb923c">
        <div class="v" style="color:#fb923c">{projA['score']}</div>
        <div class="l">Project Score</div></div>
      <div class="tile" style="--tc:#34d399">
        <div class="v" style="color:#34d399">{certA['score']}</div>
        <div class="l">Cert Score</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────
    tabs = st.tabs(["👤 Profile", "🛠 Skills", "📊 ATS Score",
                    "🔮 Role Fit", "📈 Analytics", "📚 Learning", "📥 Report"])

    # ══ TAB 1: Profile ════════════════════════════════════════════════
    with tabs[0]:
        a, b = st.columns(2)
        with a:
            st.markdown('<div class="sh">👤 Personal Info</div>', unsafe_allow_html=True)
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            for k, v in [("Name", parsed["name"]), ("Email", parsed["email"]),
                          ("Phone", parsed["phone"]),
                          ("Level", f"{explvl['level']} — {explvl['description']}")]:
                st.markdown(f'<div class="ir"><span class="ik">{k}</span><span class="iv">{v}</span></div>',
                            unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sh">🎓 Education</div>', unsafe_allow_html=True)
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            if parsed["education"]:
                for e in parsed["education"]: st.markdown(f"• {e}")
            else: st.caption("Not detected — check PDF formatting.")
            st.markdown('</div>', unsafe_allow_html=True)

        with b:
            st.markdown('<div class="sh">💼 Experience</div>', unsafe_allow_html=True)
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            if parsed["experience"]:
                for e in parsed["experience"]: st.markdown(f"• {e}")
            else: st.caption("Not detected.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sh">🏗 Projects</div>', unsafe_allow_html=True)
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            if parsed["projects"]:
                for p in parsed["projects"]: st.markdown(f"• {p}")
            else: st.caption("No projects detected.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sh">🏆 Certifications</div>', unsafe_allow_html=True)
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            if parsed["certifications"]:
                for c in parsed["certifications"]: st.markdown(f"• {c}")
            else: st.caption("No certifications detected.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ══ TAB 2: Skills ═════════════════════════════════════════════════
    with tabs[1]:
        sa, sb = st.columns([3, 2])
        with sa:
            st.markdown('<div class="sh">✅ Skills Found in Resume</div>', unsafe_allow_html=True)
            if fskills:
                for cat, skills in fskills.items():
                    st.markdown(f"**{cat}**")
                    st.markdown("".join(f'<span class="pill pg">{s}</span>' for s in skills),
                                unsafe_allow_html=True)
                    st.markdown("")
            else:
                st.warning("No skills matched. Ensure standard skill names are used (Python, React, AWS, etc.).")
        with sb:
            st.markdown(f'<div class="sh">❌ Missing for {target_role}</div>', unsafe_allow_html=True)
            if mskills:
                st.markdown("".join(f'<span class="pill pr">{s}</span>' for s in mskills),
                            unsafe_allow_html=True)
                st.caption(f"Add {len(mskills)} skills to strengthen your profile.")
            else:
                st.success("🎉 All key skills present for this role!")

    # ══ TAB 3: ATS Score ══════════════════════════════════════════════
    with tabs[2]:
        if not jd_text:
            st.info("ℹ️ Upload a Job Description PDF to get your ATS score. Without it, only resume structure is evaluated.")
        else:
            av = ats["ats_score"]
            if av >= 70:
                bg, bc, fc, grade = "rgba(34,197,94,.08)","rgba(34,197,94,.28)","#4ade80","🟢 Strong Match"
            elif av >= 45:
                bg, bc, fc, grade = "rgba(234,179,8,.08)","rgba(234,179,8,.28)","#facc15","🟡 Moderate Match"
            else:
                bg, bc, fc, grade = "rgba(239,68,68,.08)","rgba(239,68,68,.28)","#f87171","🔴 Weak Match"

            st.markdown(f"""
            <div class="ats-banner" style="background:{bg};border-color:{bc}">
              <div class="ats-num" style="color:{fc}">{av}%</div>
              <div>
                <div class="ats-grade" style="color:{fc}">{grade}</div>
                <div class="ats-hint" style="color:{fc}">
                  4-signal scoring · skill match, keyword recall, domain alignment, achievements
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            x1, x2 = st.columns(2)
            with x1:
                st.markdown('<div class="sh">📊 Signal Breakdown</div>', unsafe_allow_html=True)
                for lbl, val, tip in [
                    ("🛠 Skill Overlap",    ats["skill_match_pct"],   "30% · resume skills vs JD skills"),
                    ("🔑 JD Keywords",      ats["keyword_match_pct"], "30% · JD-distinctive keyword recall"),
                    ("🎯 Domain Alignment", ats["s3"],                "25% · domain fingerprint cosine"),
                    ("📊 Achievements",     ats["s4"],                "15% · numbers, %, impact verbs"),
                ]:
                    c = "#22c55e" if val >= 65 else ("#f59e0b" if val >= 40 else "#ef4444")
                    st.markdown(f"""
                    <div class="sig">
                      <div class="sig-row"><span>{lbl}</span>
                        <span style="color:{c};font-weight:700">{val}%</span></div>
                      <div class="sig-bg">
                        <div class="sig-fill" style="width:{min(val,100)}%;background:{c}"></div>
                      </div>
                      <div class="sig-tip">{tip}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown('<div class="sh">💡 Recommendations</div>', unsafe_allow_html=True)
                for rec in ats["recommendations"]:
                    st.markdown(f'<div class="fb-i">{rec}</div>', unsafe_allow_html=True)

            with x2:
                st.markdown('<div class="sh">🔑 Missing JD Keywords</div>', unsafe_allow_html=True)
                if ats["missing_keywords"]:
                    st.markdown(
                        "".join(f'<span class="pill pr">{k}</span>'
                                for k in ats["missing_keywords"][:20]),
                        unsafe_allow_html=True)
                    st.caption(f"{len(ats['missing_keywords'])} missing — add them to boost score.")
                else:
                    st.success("No critical keywords missing!")

    # ══ TAB 4: Role Fit ═══════════════════════════════════════════════
    with tabs[3]:
        top  = rpred["top_role"]
        conf = rpred["confidences"]
        st.markdown('<div class="sh">🏆 Best Role Match</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass" style="border-color:rgba(99,102,241,.3)">
          <div style="font-size:1.3rem;font-weight:800;color:#e2e8f0">🎯 {top}</div>
          <div style="color:#818cf8;font-weight:700;font-size:1rem;margin-top:3px">
            {conf[top]}% confidence
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="sh">📊 All Roles</div>', unsafe_allow_html=True)
        for role, pct in sorted(conf.items(), key=lambda x: -x[1]):
            c  = "#818cf8" if role == top else "#1e293b"
            fw = "700" if role == top else "400"
            st.markdown(f"""
            <div class="rb">
              <div class="rb-row" style="color:{c};font-weight:{fw}">
                <span>{'🏆 ' if role==top else ''}{role}</span><span>{pct}%</span>
              </div>
              <div class="rb-bg">
                <div class="rb-fill" style="width:{pct}%;background:{c}"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ══ TAB 5: Analytics ══════════════════════════════════════════════
    with tabs[4]:
        BG   = "rgba(255,255,255,0.02)"
        FC   = "#94a3b8"
        GRID = "rgba(255,255,255,0.04)"

        r1, r2 = st.columns(2)
        av_g   = ats["ats_score"] if jd_text else rscore["total"]
        gtitle = "ATS Score" if jd_text else "Resume Score"

        with r1:
            fg = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=av_g,
                title={"text": gtitle, "font": {"size": 13, "color": FC}},
                delta={"reference": 70,
                       "increasing": {"color": "#22c55e"},
                       "decreasing": {"color": "#ef4444"}},
                number={"font": {"color": "#e2e8f0", "size": 40}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": FC, "tickfont": {"color": FC}},
                    "bar":  {"color": "#3b82f6", "thickness": 0.3},
                    "bgcolor": "rgba(255,255,255,0.03)",
                    "bordercolor": "rgba(255,255,255,0.05)",
                    "steps": [
                        {"range": [0, 40],   "color": "rgba(239,68,68,0.08)"},
                        {"range": [40, 70],  "color": "rgba(234,179,8,0.08)"},
                        {"range": [70, 100], "color": "rgba(34,197,94,0.08)"},
                    ],
                    "threshold": {"line": {"color": "#22c55e", "width": 3}, "value": 70}
                }
            ))
            fg.update_layout(height=270, paper_bgcolor=BG, font_color=FC,
                             margin=dict(l=20, r=20, t=50, b=10))
            st.plotly_chart(fg, use_container_width=True)

        with r2:
            if fskills and len(fskills) > 0 and any(len(v) > 0 for v in fskills.values()):
                fp = px.pie(
                    values=[len(v) for v in fskills.values()],
                    names=list(fskills.keys()), hole=0.45,
                    title="Skill Distribution",
                    color_discrete_sequence=["#3b82f6","#818cf8","#22c55e",
                                             "#f59e0b","#ef4444","#38bdf8","#a78bfa"]
                )
                fp.update_traces(textfont_color="#e2e8f0")
                fp.update_layout(height=270, paper_bgcolor=BG, font_color=FC,
                                  margin=dict(l=10, r=10, t=50, b=10),
                                  legend=dict(font=dict(color=FC)))
                st.plotly_chart(fp, use_container_width=True)
            else:
                st.info("No skills found to display distribution.")

        r3, r4 = st.columns(2)
        with r3:
            if conf and len(conf) > 0:
                top10 = dict(sorted(conf.items(), key=lambda x: -x[1])[:10])
                fb = go.Figure(go.Bar(
                    x=list(top10.values()), y=list(top10.keys()), orientation='h',
                    marker=dict(color=list(top10.values()),
                                colorscale=[[0,"#1e3a5f"],[1,"#60a5fa"]],
                                showscale=False),
                    text=[f"{v}%" for v in top10.values()], textposition="outside",
                    textfont=dict(color=FC, size=11),
                ))
                fb.update_layout(
                    title=dict(text="Top Role Matches", font=dict(color=FC)),
                    height=300, paper_bgcolor=BG, plot_bgcolor="rgba(0,0,0,0)",
                    font_color=FC, showlegend=False,
                    margin=dict(l=10, r=60, t=50, b=10),
                    xaxis=dict(gridcolor=GRID, tickfont=dict(color=FC)),
                    yaxis=dict(tickfont=dict(color=FC))
                )
                st.plotly_chart(fb, use_container_width=True)

        with r4:
            fbar = go.Figure(go.Bar(
                x=["Skills", "Projects", "Certs", "ATS", "Overall"],
                y=[rscore["skill_score"], projA["score"], certA["score"],
                   ats["ats_score"], rscore["total"]],
                marker_color=["#3b82f6","#22c55e","#8b5cf6","#f59e0b","#ec4899"],
                text=[rscore["skill_score"], projA["score"], certA["score"],
                      ats["ats_score"], rscore["total"]],
                textposition="outside",
                textfont=dict(color=FC, size=11),
            ))
            fbar.update_layout(
                title=dict(text="Score Breakdown", font=dict(color=FC)),
                height=300, paper_bgcolor=BG, plot_bgcolor="rgba(0,0,0,0)",
                font_color=FC, margin=dict(l=10, r=10, t=50, b=10),
                xaxis=dict(gridcolor=GRID, tickfont=dict(color=FC)),
                yaxis=dict(range=[0, 115], gridcolor=GRID, tickfont=dict(color=FC))
            )
            st.plotly_chart(fbar, use_container_width=True)

        if fskills and len(fskills) > 0 and any(len(v) > 0 for v in fskills.values()):
            df  = pd.DataFrame({"Category": list(fskills.keys()),
                                 "Count":    [len(v) for v in fskills.values()]})
            fc2 = px.bar(df, x="Category", y="Count",
                         title="Skills Found per Category",
                         color="Count",
                         color_continuous_scale=[[0,"#1e3a5f"],[1,"#60a5fa"]],
                         text="Count")
            fc2.update_traces(textposition="outside", textfont=dict(color=FC))
            fc2.update_layout(
                height=280, paper_bgcolor=BG, plot_bgcolor="rgba(0,0,0,0)",
                font_color=FC, margin=dict(l=10, r=10, t=50, b=40),
                xaxis=dict(tickangle=-30, gridcolor=GRID, tickfont=dict(color=FC)),
                yaxis=dict(gridcolor=GRID, tickfont=dict(color=FC))
            )
            st.plotly_chart(fc2, use_container_width=True)

        if jd_text:
            sv = [ats["s1"], ats["s2"], ats["s3"], ats["s4"]]
            sl = ["Skill Overlap", "JD Keywords", "Domain Align", "Achievements"]
            fr = go.Figure(go.Scatterpolar(
                r=sv + [sv[0]], theta=sl + [sl[0]], fill="toself",
                fillcolor="rgba(59,130,246,0.1)",
                line=dict(color="#60a5fa", width=2),
                marker=dict(color="#60a5fa", size=6)
            ))
            fr.update_layout(
                title=dict(text="ATS Signal Radar", font=dict(color=FC)),
                polar=dict(
                    bgcolor="rgba(255,255,255,0.02)",
                    radialaxis=dict(visible=True, range=[0, 100],
                                   gridcolor=GRID, tickfont=dict(color=FC)),
                    angularaxis=dict(gridcolor=GRID, tickfont=dict(color=FC))
                ),
                height=300, paper_bgcolor=BG, font_color=FC,
                margin=dict(l=30, r=30, t=60, b=20)
            )
            st.plotly_chart(fr, use_container_width=True)

    # ══ TAB 6: Learning ═══════════════════════════════════════════════
    with tabs[5]:
        st.markdown('<div class="sh">📚 Personalized Learning Roadmap</div>', unsafe_allow_html=True)
        if not mskills:
            st.success("🎉 You have all key skills for this role! Focus on: projects, certifications, and ATS optimization.")
        else:
            st.markdown("".join(f'<span class="pill pr">{s}</span>' for s in mskills),
                        unsafe_allow_html=True)
            st.markdown(f"<br><small style='color:#334155'>{len(mskills)} missing skills · courses below</small><br>",
                        unsafe_allow_html=True)
        
        if recs:
            for i, r in enumerate(recs, 1):
                with st.expander(f"📖 {r['skill'].title()} — {r['course']}", expanded=i <= 3):
                    cc1, cc2 = st.columns([3, 1])
                    with cc1:
                        st.markdown(f"**Course:** {r['course']}")
                        st.markdown(f"**Platform:** `{r['platform']}`")
                    with cc2:
                        st.link_button("Open →", r["url"], use_container_width=True)
        else:
            st.info("💡 No course recommendations found. Try searching manually on Coursera or Udemy for your missing skills.")

    # ══ TAB 7: Report ═════════════════════════════════════════════════
    with tabs[6]:
        st.markdown('<div class="sh">📥 Download Full PDF Report</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("""
Your report includes:
- ✅ Resume score & ATS signal breakdown · 🔮 Role prediction (24 roles)
- 🛠 Skills found & missing skills · 📚 Course recommendations
- 🏆 Certifications & project analysis
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("Generating PDF…"):
            pdf = generate_pdf_report(
                parsed, fskills, mskills, ats, rpred,
                explvl, projA, certA, recs, rscore
            )

        name = parsed["name"].replace(" ", "_") if parsed["name"] != "Not detected" else "candidate"
        st.download_button(
            "📥 Download PDF Report", data=pdf,
            file_name=f"scoremyresume_{name}.pdf",
            mime="application/pdf",
            use_container_width=True, type="primary"
        )
        st.caption("Generated locally — your data never leaves this session.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#0f172a;font-size:.67rem;margin-top:2.5rem;
            padding-top:1rem;border-top:1px solid rgba(255,255,255,0.04)'>
  🎯 ScoreMyResume v2.1 · Python · Streamlit · spaCy · Scikit-learn · Plotly · Production Ready
</div>""", unsafe_allow_html=True)
