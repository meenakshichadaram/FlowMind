import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database.session import init_db, SessionLocal
from app.memory.memory_manager import MemoryManager
from app.services.orchestrator import IntelligenceOrchestrator
from app.graph.workflow import flowmind_graph
from app.ui.theme import inject_theme, risk_badge_html

st.set_page_config(
    page_title="FlowMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

# Ensure DB is initialized
init_db()

db = SessionLocal()
try:
    mem = MemoryManager(db)
    orchestrator = IntelligenceOrchestrator(db)
    user = mem.get_user_profile(user_id=1)
    user_name = user.name if user else "Student"

    # ------------------------------------------------------------------
    # Sidebar — feels like an OS shell, not a list of tools
    # ------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### 🧠 FlowMind AI")
        st.caption("Your AI operating system for learning")
        st.markdown("---")
        st.markdown(f"**{user_name}**")
        snapshot = mem.get_full_student_memory_snapshot()
        st.caption(f"Daily goal: {snapshot['daily_goal_hours']} hrs · Focus avg: {round(snapshot['recent_focus_avg'], 1)}/100")
        st.markdown("---")
        st.caption(
            "FlowMind continuously watches your unfinished work, deadlines, "
            "concepts, and focus patterns, and tells you the one thing worth "
            "doing right now."
        )

    # ------------------------------------------------------------------
    # Greeting + Today's Situation
    # ------------------------------------------------------------------
    st.markdown(f'<div class="fm-greeting">{orchestrator.greeting()}, {user_name}.</div>', unsafe_allow_html=True)
    st.markdown('<div class="fm-subtitle">Here is today\'s learning situation.</div>', unsafe_allow_html=True)

    bullets = orchestrator.situation_bullets(user_id=1)
    bullets_html = "".join(f'<div class="fm-situation-item">• {b}</div>' for b in bullets)
    st.markdown(f'<div class="fm-card">{bullets_html}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Today's Focus — the single primary recommendation
    # ------------------------------------------------------------------
    rec = orchestrator.primary_recommendation(user_id=1)
    st.markdown('<div class="fm-eyebrow">Today\'s Focus</div>', unsafe_allow_html=True)
    time_html = (
        f'<div class="fm-hero-time">⏱ Estimated time: {rec["estimated_minutes"]} minutes</div>'
        if rec.get("estimated_minutes")
        else ""
    )
    st.markdown(
        f"""
        <div class="fm-hero-card">
            <div class="fm-hero-label">Recommended Next Action</div>
            <div class="fm-hero-title">{rec['title']}</div>
            <div class="fm-hero-reason"><b>Reason:</b> {rec['reason']}</div>
            {time_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Row: Recovered Intentions + Deadline Radar
    # ------------------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="fm-section-title">🔁 Recovered Intentions</div>', unsafe_allow_html=True)
        intentions = orchestrator.recovered_intentions(user_id=1, limit=3)
        if intentions:
            timeline_html = '<div class="fm-timeline">'
            for item in intentions:
                timeline_html += f"""
                <div class="fm-timeline-node">
                    <div class="fm-timeline-when">{item['last_accessed_human']}</div>
                    <div class="fm-timeline-title">{item['title']}</div>
                    <div class="fm-timeline-detail">
                        {item['source_type']} · {int(item['progress_percent'])}% complete<br>
                        Suggested: {item['suggested_action']} (~{item['estimated_minutes']} min)
                    </div>
                </div>
                """
            timeline_html += "</div>"
            st.markdown(f'<div class="fm-card">{timeline_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="fm-card">Nothing sitting abandoned right now — nice work.</div>', unsafe_allow_html=True)
        st.page_link("pages/1_Recovered_Intentions.py", label="Open Recovered Intentions", icon="🔁")

    with col2:
        st.markdown('<div class="fm-section-title">📡 Deadline Radar</div>', unsafe_allow_html=True)
        radar = orchestrator.deadline_radar(user_id=1, limit=3)
        if radar:
            radar_html = ""
            for r in radar:
                radar_html += f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:0.55rem 0; border-bottom:1px dashed rgba(255,255,255,0.08);">
                    <div>
                        <div style="font-weight:700; color:#f0f3fa;">{r['title']}</div>
                        <div style="color:#9aa4b2; font-size:0.82rem;">
                            Due in {r['due_in']} · {int(r['completion_probability']*100)}% completion probability · ~{r['estimated_completion']} of work
                        </div>
                    </div>
                    <div>{risk_badge_html(r['risk_label'])}</div>
                </div>
                """
            st.markdown(f'<div class="fm-card">{radar_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="fm-card">No deadlines currently tracked.</div>', unsafe_allow_html=True)
        st.page_link("pages/2_Deadline_Radar.py", label="Open Deadline Radar", icon="📡")

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Row: Knowledge Journey + Productivity Insights
    # ------------------------------------------------------------------
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="fm-section-title">🗺️ Knowledge Journey</div>', unsafe_allow_html=True)
        chain = orchestrator.knowledge_chain(limit=6)
        chain_html = '<div class="fm-chain">'
        for i, node in enumerate(chain):
            chain_html += f'<div class="fm-chain-node">{node}</div>'
            if i < len(chain) - 1:
                chain_html += '<div class="fm-chain-arrow">→</div>'
        chain_html += "</div>"
        st.markdown(f'<div class="fm-card">{chain_html}</div>', unsafe_allow_html=True)
        st.page_link("pages/3_Knowledge_Journey.py", label="Explore Knowledge Journey", icon="🗺️")

    with col4:
        st.markdown('<div class="fm-section-title">📈 Productivity Insights</div>', unsafe_allow_html=True)
        insights = orchestrator.productivity_insights(user_id=1)
        insights_html = "".join(f'<div class="fm-situation-item">💡 {i}</div>' for i in insights)
        st.markdown(f'<div class="fm-card">{insights_html}</div>', unsafe_allow_html=True)
        st.page_link("pages/4_Productivity_Insights.py", label="See all Productivity Insights", icon="📈")

    st.markdown("---")

    # ------------------------------------------------------------------
    # Memory made visible
    # ------------------------------------------------------------------
    st.markdown('<div class="fm-section-title">🧠 What FlowMind remembers about you</div>', unsafe_allow_html=True)
    memory_bits = []
    if snapshot["top_unfinished"]:
        memory_bits.append(f"Top of mind: {', '.join(snapshot['top_unfinished'][:2])}")
    if snapshot["high_risk_deadlines"]:
        memory_bits.append(f"Watching closely: {', '.join(snapshot['high_risk_deadlines'][:2])}")
    memory_bits.append(f"Recent focus average: {round(snapshot['recent_focus_avg'], 1)}/100")
    chips_html = "".join(f'<span class="fm-memory-chip">{b}</span>' for b in memory_bits)
    st.markdown(chips_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Ask FlowMind — the single conversational entry point (LangGraph)
    # ------------------------------------------------------------------
    st.markdown('<div class="fm-section-title">⚡ Ask FlowMind</div>', unsafe_allow_html=True)
    st.caption("One assistant, everything it knows about your learning journey.")

    query_input = st.text_input(
        "Ask FlowMind:",
        placeholder="e.g., What should I prioritize before my internship deadline?",
        key="global_query",
        label_visibility="collapsed",
    )

    if st.button("Ask FlowMind", type="primary"):
        if not query_input.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking across your unfinished work, deadlines, knowledge base, and focus patterns..."):
                initial_state = {
                    "user_id": 1,
                    "query": query_input,
                    "engine_hint": "auto",
                    "intent_detected": "pending",
                    "memory_snapshot": {},
                    "need_rag": False,
                    "retrieved_docs": [],
                    "need_tool": False,
                    "tool_to_execute": None,
                    "tool_input_args": {},
                    "tool_execution_result": None,
                    "tools_executed": [],
                    "reasoning": "",
                    "final_response": "",
                    "memory_updates": {},
                }
                try:
                    res = flowmind_graph.invoke(initial_state)
                    st.markdown(f'<div class="fm-card">{res.get("final_response", "No response generated.")}</div>', unsafe_allow_html=True)
                    with st.expander("How FlowMind reasoned about this"):
                        st.markdown(f"**Intent Detected**: `{res.get('intent_detected', 'general')}`")
                        st.markdown(f"**Tools Used**: `{res.get('tools_executed', [])}`")
                        st.markdown(f"**Reasoning**: {res.get('reasoning', '')}")
                        docs = res.get("retrieved_docs", [])
                        if docs:
                            st.markdown("**Referenced knowledge:**")
                            for d in docs:
                                st.markdown(f"- `{d.source_name}` (relevance {d.score})")
                except Exception as e:
                    st.error(f"FlowMind couldn't complete that request: {e}")

finally:
    db.close()
