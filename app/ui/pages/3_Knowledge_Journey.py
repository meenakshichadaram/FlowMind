import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.database.session import SessionLocal
from app.services.knowledge_fusion import KnowledgeFusionEngine
from app.services.orchestrator import IntelligenceOrchestrator
from app.ui.theme import inject_theme

st.set_page_config(page_title="Knowledge Journey - FlowMind AI", page_icon="🗺️", layout="wide")
inject_theme()

st.markdown('<div class="fm-greeting">Knowledge Journey</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="fm-subtitle">Not a document search box — an explorer of how everything you\'ve learned connects.</div>',
    unsafe_allow_html=True,
)

db = SessionLocal()
try:
    engine = KnowledgeFusionEngine(db)
    orchestrator = IntelligenceOrchestrator(db)

    st.markdown('<div class="fm-section-title">🧭 Your current learning path</div>', unsafe_allow_html=True)
    chain = orchestrator.knowledge_chain(limit=8)
    chain_html = '<div class="fm-chain">'
    for i, node in enumerate(chain):
        chain_html += f'<div class="fm-chain-node">{node}</div>'
        if i < len(chain) - 1:
            chain_html += '<div class="fm-chain-arrow">→</div>'
    chain_html += "</div>"
    st.markdown(f'<div class="fm-card">{chain_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="fm-section-title">🔎 Explore a concept</div>', unsafe_allow_html=True)

    default_topic = chain[0] if chain else "Attention Mechanism and Transformer Architecture"
    query = st.text_input("Which topic do you want to explore?", value=default_topic, key="fusion_query")

    if st.button("Explore this concept", type="primary"):
        with st.spinner("Tracing related concepts, prerequisites, and everything you've connected to this topic..."):
            res = engine.fuse_knowledge_query(query=query)
            graph = res["graph"]
            chunks = res["retrieved_chunks"]

            related = [n.label for n in graph.nodes if n.label.lower() != query.lower()]
            prerequisites = [e.source for e in graph.edges if e.relationship == "prerequisite" and e.target.lower() == query.lower()]
            next_topics = [e.target for e in graph.edges if e.source.lower() == query.lower()]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="fm-eyebrow">Related Concepts</div>', unsafe_allow_html=True)
                if related:
                    chips = "".join(f'<span class="fm-memory-chip">{r}</span>' for r in related[:8])
                    st.markdown(f'<div class="fm-card">{chips}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="fm-card">No linked concepts yet for this topic.</div>', unsafe_allow_html=True)

                st.markdown('<div class="fm-eyebrow">Prerequisites</div>', unsafe_allow_html=True)
                if prerequisites:
                    chips = "".join(f'<span class="fm-memory-chip">{p}</span>' for p in prerequisites)
                    st.markdown(f'<div class="fm-card">{chips}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="fm-card">Nothing prerequisite is tracked yet.</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="fm-eyebrow">Recommended Next Topic</div>', unsafe_allow_html=True)
                if next_topics:
                    chips = "".join(f'<span class="fm-memory-chip">{n}</span>' for n in next_topics)
                    st.markdown(f'<div class="fm-card">{chips}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="fm-card">Explore more topics to build out this path.</div>', unsafe_allow_html=True)

                st.markdown('<div class="fm-eyebrow">Learning Path</div>', unsafe_allow_html=True)
                path_html = " → ".join(graph.revision_path) if graph.revision_path else "Not enough data yet"
                st.markdown(f'<div class="fm-card">{path_html}</div>', unsafe_allow_html=True)

            st.markdown('<div class="fm-eyebrow">Synthesis</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="fm-card">{graph.summary}</div>', unsafe_allow_html=True)

            st.markdown('<div class="fm-eyebrow">Previous Notes & Sources You\'ve Connected Here</div>', unsafe_allow_html=True)
            if chunks:
                for c in chunks:
                    st.markdown(
                        f'<div class="fm-card"><b>{c.source_name}</b> <span style="color:#7c8598;">({c.source_type}, relevance {round(c.score,2)})</span><br>{c.content}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<div class="fm-card">No indexed notes yet — upload documents to build this out.</div>', unsafe_allow_html=True)

finally:
    db.close()
