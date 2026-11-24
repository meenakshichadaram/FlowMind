import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.database.session import SessionLocal
from app.services.deadline_intelligence import DeadlineIntelligenceEngine
from app.services.orchestrator import IntelligenceOrchestrator
from app.ui.theme import inject_theme, risk_badge_html, progress_ring_html

st.set_page_config(page_title="Deadline Radar - FlowMind AI", page_icon="📡", layout="wide")
inject_theme()

st.markdown('<div class="fm-greeting">Deadline Radar</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="fm-subtitle">Not reminders — predictions. FlowMind estimates whether you\'ll actually finish in time.</div>',
    unsafe_allow_html=True,
)

db = SessionLocal()
try:
    engine = DeadlineIntelligenceEngine(db)
    orchestrator = IntelligenceOrchestrator(db)
    radar = orchestrator.deadline_radar(user_id=1, limit=20)

    if radar:
        for r in radar:
            ring_color = "#f87171" if r["risk_label"] == "Critical" else "#fbbf24" if r["risk_label"] == "Elevated" else "#4ade80"
            st.markdown(
                f"""
                <div class="fm-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;">
                        <div class="fm-ring-wrap">
                            {progress_ring_html(r['completion_probability'] * 100, ring_color)}
                            <div>
                                <div style="font-weight:700; font-size:1.05rem; color:#f0f3fa;">{r['title']}</div>
                                <div style="color:#9aa4b2; font-size:0.85rem;">{r['course_or_project']} · due in {r['due_in']}</div>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            {risk_badge_html(r['risk_label'])}
                            <div style="color:#9aa4b2; font-size:0.8rem; margin-top:0.35rem;">~{r['estimated_completion']} of work remaining</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="fm-card">No deadlines currently tracked.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="fm-section-title">🔮 Ask FlowMind to forecast a specific deadline</div>', unsafe_allow_html=True)
    st.caption("Get a probability, an explanation, and a day-by-day recommended schedule.")

    tasks = engine.get_all_deadlines(user_id=1)
    if tasks:
        selected_id = st.selectbox(
            "Choose a task:",
            [t.id for t in tasks],
            format_func=lambda x: next(t.title for t in tasks if t.id == x),
        )

        if st.button("Forecast completion", type="primary"):
            with st.spinner("Modeling your pace, complexity, and available time..."):
                pred = engine.evaluate_task_risk(task_id=selected_id)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Completion Probability", f"{int(pred.completion_probability * 100)}%")
                with c2:
                    st.metric("Risk Score", f"{pred.risk_score} / 100", pred.risk_level)
                with c3:
                    st.metric("Predicted Finish Date", pred.predicted_finish_date)

                st.markdown(f'<div class="fm-card"><b>Reason:</b> {pred.explanation}</div>', unsafe_allow_html=True)

                st.markdown('<div class="fm-section-title">📅 Suggested Plan</div>', unsafe_allow_html=True)
                if pred.recommended_schedule:
                    plan_html = '<div class="fm-timeline">'
                    for day in pred.recommended_schedule:
                        plan_html += f"""
                        <div class="fm-timeline-node">
                            <div class="fm-timeline-when">{day['day']} · {day['date']}</div>
                            <div class="fm-timeline-detail">{day['focus_topic']} — {day['recommended_hours']} hrs</div>
                        </div>
                        """
                    plan_html += "</div>"
                    st.markdown(f'<div class="fm-card">{plan_html}</div>', unsafe_allow_html=True)
    else:
        st.write("No deadline tasks registered.")

finally:
    db.close()
