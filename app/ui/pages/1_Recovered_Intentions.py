import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.database.session import SessionLocal
from app.services.intent_recovery import IntentRecoveryEngine
from app.services.orchestrator import IntelligenceOrchestrator
from app.ui.theme import inject_theme

st.set_page_config(page_title="Recovered Intentions - FlowMind AI", page_icon="🔁", layout="wide")
inject_theme()

st.markdown('<div class="fm-greeting">Recovered Intentions</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="fm-subtitle">Everything you started and drifted away from — resurfaced, explained, and ready to resume.</div>',
    unsafe_allow_html=True,
)

db = SessionLocal()
try:
    engine = IntentRecoveryEngine(db)
    orchestrator = IntelligenceOrchestrator(db)

    intentions = orchestrator.recovered_intentions(user_id=1, limit=20)

    if intentions:
        timeline_html = '<div class="fm-timeline">'
        for item in intentions:
            timeline_html += f"""
            <div class="fm-timeline-node">
                <div class="fm-timeline-when">{item['last_accessed_human']}</div>
                <div class="fm-timeline-title">{item['title']}</div>
                <div class="fm-timeline-detail">
                    {item['source_type']} · {int(item['progress_percent'])}% complete · revisited {item['revisit_count']} time(s)<br>
                    <b>Suggested:</b> {item['suggested_action']}<br>
                    <b>Estimated time:</b> ~{item['estimated_minutes']} minutes
                </div>
            </div>
            """
        timeline_html += "</div>"
        st.markdown(f'<div class="fm-card">{timeline_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="fm-card">Nothing sitting abandoned right now — nice work.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("💬 Get FlowMind's deeper reasoning on why these matter"):
        if st.button("Analyze with AI"):
            with st.spinner("Reviewing decay scores, revisit patterns, and priority signals..."):
                res = engine.analyze_unfinished_work(user_id=1)
                st.markdown(f'<div class="fm-card">{res.workflow_summary}</div>', unsafe_allow_html=True)
                st.markdown(f"**Top recommended action:** {res.recommended_next_step}")

    st.markdown("---")
    st.markdown('<div class="fm-section-title">➕ Flag something you started</div>', unsafe_allow_html=True)
    st.caption("Tell FlowMind about a PDF, video, article, project, or note you haven't finished.")

    with st.form("new_activity_form"):
        title = st.text_input("Title of Activity / Resource", placeholder="e.g., Attention Is All You Need Paper")
        col1, col2 = st.columns(2)
        with col1:
            stype = st.selectbox("Source Type", ["PDF", "Video", "Article", "App", "Code", "Note"])
            progress = st.slider("Current Progress %", 0.0, 100.0, 25.0)
        with col2:
            url_path = st.text_input("URL or File Path (Optional)")
            reason = st.text_input("Why is this important?", placeholder="Required for ML exam")

        action = st.text_input("Suggested next step", placeholder="Read pages 4-6 on Multi-Head Attention")
        submitted = st.form_submit_button("Add to memory")

        if submitted and title:
            item = engine.register_new_unfinished_item(
                title=title,
                source_type=stype,
                url_or_path=url_path,
                progress=progress,
                reason=reason,
                action=action,
            )
            st.success(f"FlowMind will now track '{item.title}'.")
            st.rerun()

finally:
    db.close()
