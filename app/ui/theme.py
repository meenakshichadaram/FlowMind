"""Shared design system for FlowMind AI's Streamlit frontend.

Centralizing the CSS here keeps every screen visually consistent — the same
dark, premium, Notion-AI / Linear / Cursor-inspired language — without
duplicating a giant style block in each page file.
"""

import streamlit as st

THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #141a24 0%, #0b0e14 45%, #0a0c11 100%);
        color: #d8dde5;
    }

    section[data-testid="stSidebar"] {
        background: #0d1117;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Kill default streamlit top padding for a tighter, app-like feel */
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }

    /* ---------- Typography ---------- */
    .fm-greeting {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #a78bfa, #f472b6 45%, #38bdf8 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .fm-subtitle { color: #8b949e; font-size: 1rem; margin-bottom: 1.4rem; }
    .fm-section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e6e9ef;
        margin: 0.2rem 0 0.7rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .fm-eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.72rem;
        color: #7c8598;
        font-weight: 700;
    }

    /* ---------- Cards ---------- */
    .fm-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.15rem 1.3rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        margin-bottom: 0.9rem;
    }
    .fm-card:hover { border-color: rgba(167,139,250,0.35); }

    .fm-hero-card {
        background: linear-gradient(135deg, rgba(124,58,237,0.16), rgba(56,189,248,0.08));
        border: 1px solid rgba(167,139,250,0.35);
        border-radius: 20px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 20px 50px rgba(88,45,222,0.15);
    }
    .fm-hero-label { color: #c4b5fd; font-weight: 700; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; }
    .fm-hero-title { font-size: 1.5rem; font-weight: 800; color: #f4f2ff; margin: 0.35rem 0 0.5rem 0; }
    .fm-hero-reason { color: #c9d1d9; font-size: 0.94rem; line-height: 1.5; }
    .fm-hero-time {
        display: inline-block; margin-top: 0.7rem; padding: 0.3rem 0.75rem;
        border-radius: 999px; background: rgba(56,189,248,0.14); color: #7dd3fc;
        font-weight: 700; font-size: 0.82rem; border: 1px solid rgba(56,189,248,0.3);
    }

    /* ---------- Situation bullets ---------- */
    .fm-situation-item {
        padding: 0.55rem 0;
        border-bottom: 1px dashed rgba(255,255,255,0.08);
        font-size: 0.95rem;
        color: #c9d1d9;
    }
    .fm-situation-item:last-child { border-bottom: none; }
    .fm-situation-item b { color: #f0f3fa; }

    /* ---------- Badges ---------- */
    .fm-badge { padding: 3px 11px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; border: 1px solid; display: inline-block; }
    .fm-badge-critical { color: #f87171; background: rgba(248,113,113,0.12); border-color: rgba(248,113,113,0.35); }
    .fm-badge-elevated { color: #fbbf24; background: rgba(251,191,36,0.12); border-color: rgba(251,191,36,0.35); }
    .fm-badge-ontrack { color: #4ade80; background: rgba(74,222,128,0.12); border-color: rgba(74,222,128,0.35); }
    .fm-badge-neutral { color: #93c5fd; background: rgba(147,197,253,0.12); border-color: rgba(147,197,253,0.35); }

    /* ---------- Timeline (Recovered Intentions) ---------- */
    .fm-timeline { border-left: 2px solid rgba(167,139,250,0.35); margin-left: 0.6rem; padding-left: 1.3rem; }
    .fm-timeline-node {
        position: relative; padding-bottom: 1.3rem;
    }
    .fm-timeline-node::before {
        content: ""; position: absolute; left: -1.62rem; top: 0.3rem;
        width: 10px; height: 10px; border-radius: 50%;
        background: #a78bfa; box-shadow: 0 0 0 4px rgba(167,139,250,0.18);
    }
    .fm-timeline-when { color: #7c8598; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; }
    .fm-timeline-title { font-size: 1.02rem; font-weight: 700; color: #f0f3fa; margin: 0.15rem 0 0.3rem 0; }
    .fm-timeline-detail { color: #9aa4b2; font-size: 0.88rem; }

    /* ---------- Knowledge chain ---------- */
    .fm-chain { display: flex; flex-wrap: wrap; align-items: center; gap: 0.4rem; }
    .fm-chain-node {
        padding: 0.4rem 0.85rem; border-radius: 10px; font-weight: 600; font-size: 0.88rem;
        background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); color: #7dd3fc;
    }
    .fm-chain-arrow { color: #566072; font-weight: 700; }

    /* ---------- Progress ring ---------- */
    .fm-ring-wrap { display: flex; align-items: center; gap: 0.9rem; }
    .fm-ring {
        width: 54px; height: 54px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 0.82rem; color: #f0f3fa;
    }

    /* ---------- Memory chip ---------- */
    .fm-memory-chip {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 999px; padding: 0.25rem 0.75rem; font-size: 0.8rem; color: #9aa4b2; margin: 0.15rem 0.3rem 0.15rem 0;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        border-radius: 10px; border: 1px solid rgba(167,139,250,0.4);
        background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(56,189,248,0.14));
        color: #f0f3fa; font-weight: 600;
    }
    .stButton > button:hover { border-color: #a78bfa; color: #fff; }

    hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
"""


def inject_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def risk_badge_html(label: str) -> str:
    mapping = {
        "Critical": "fm-badge-critical",
        "Elevated": "fm-badge-elevated",
        "On Track": "fm-badge-ontrack",
    }
    css_class = mapping.get(label, "fm-badge-neutral")
    return f'<span class="fm-badge {css_class}">{label}</span>'


def progress_ring_html(percent: float, color: str = "#a78bfa") -> str:
    percent = max(0, min(100, percent))
    return f"""
    <div class="fm-ring" style="background: conic-gradient({color} {percent}%, rgba(255,255,255,0.08) {percent}% 100%);">
        <div style="background:#0b0e14; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center;">
            {int(percent)}%
        </div>
    </div>
    """
