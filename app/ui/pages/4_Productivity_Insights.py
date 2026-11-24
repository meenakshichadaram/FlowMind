import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.database.session import SessionLocal
from app.services.focus_intelligence import FocusIntelligenceEngine
from app.services.orchestrator import IntelligenceOrchestrator
from app.ui.theme import inject_theme

st.set_page_config(page_title="Productivity Insights - FlowMind AI", page_icon="📈", layout="wide")
inject_theme()

st.markdown('<div class="fm-greeting">Productivity Insights</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="fm-subtitle">Not graphs — plain-language patterns FlowMind noticed in how you actually work.</div>',
    unsafe_allow_html=True,
)

db = SessionLocal()
try:
    engine = FocusIntelligenceEngine(db)
    orchestrator = IntelligenceOrchestrator(db)

    insights = orchestrator.productivity_insights(user_id=1)
    insights_html = "".join(f'<div class="fm-situation-item">💡 {i}</div>' for i in insights)
    st.markdown(f'<div class="fm-card">{insights_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Get FlowMind's deeper AI analysis", type="primary"):
        with st.spinner("Analyzing distraction triggers and recommending session lengths..."):
            res = engine.analyze_focus_patterns(user_id=1)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Current Focus Score", f"{res.current_focus_score} / 100")
            with c2:
                st.metric("Productivity State", res.productivity_state)
            with c3:
                st.metric("Recommended Session", f"{res.recommended_session_mins} mins", f"{res.optimal_break_mins} min break")

            st.markdown('<div class="fm-eyebrow">Key Distraction Risks</div>', unsafe_allow_html=True)
            risk_html = "".join(f'<div class="fm-situation-item">⚠️ {r}</div>' for r in res.distraction_risks)
            st.markdown(f'<div class="fm-card">{risk_html}</div>', unsafe_allow_html=True)

            st.markdown('<div class="fm-eyebrow">Actionable Insights</div>', unsafe_allow_html=True)
            for insight in res.actionable_insights:
                st.markdown(f'<div class="fm-card">{insight}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="fm-section-title">⏱ Log a study session</div>', unsafe_allow_html=True)
    st.caption("The more sessions FlowMind sees, the sharper these insights get.")

    with st.form("log_session_form"):
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Session Duration (minutes)", min_value=10, max_value=240, value=45)
            distractions = st.number_input("Distraction Interruptions Count", min_value=0, max_value=20, value=2)
        with col2:
            tab_switches = st.number_input("Tab Switches Count", min_value=0, max_value=100, value=12)
            triggers = st.text_input("Distraction Triggers", value="Social Media, Tab Switching")

        submitted = st.form_submit_button("Record session into memory")
        if submitted:
            session = engine.log_new_focus_session(
                duration_mins=duration,
                distraction_count=distractions,
                tab_switches=tab_switches,
                triggers=triggers,
            )
            st.success(f"Session recorded! Focus Score: {session.focus_score}/100")
            st.rerun()

finally:
    db.close()
