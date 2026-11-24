import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.config.settings import settings
from app.database.session import SessionLocal
from app.services.knowledge_fusion import KnowledgeFusionEngine
from app.ui.theme import inject_theme

st.set_page_config(page_title="Upload Documents - FlowMind AI", page_icon="📁", layout="wide")
inject_theme()

st.markdown('<div class="fm-greeting">Feed FlowMind</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="fm-subtitle">Upload PDFs, notes, or docs — FlowMind indexes them so your Knowledge Journey keeps growing.</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a file to index:",
    type=["pdf", "txt", "md", "html", "py", "json"],
)

if uploaded_file is not None:
    st.markdown(
        f'<div class="fm-card"><b>{uploaded_file.name}</b> · {round(uploaded_file.size/1024, 1)} KB</div>',
        unsafe_allow_html=True,
    )

    if st.button("Process & index this file", type="primary"):
        with st.spinner("Extracting text, chunking, and embedding into memory..."):
            save_path = Path(settings.UPLOAD_DIR) / uploaded_file.name
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            db = SessionLocal()
            try:
                engine = KnowledgeFusionEngine(db)
                chunk_count = engine.index_document(str(save_path))

                if chunk_count > 0:
                    st.success(f"Indexed '{uploaded_file.name}' into {chunk_count} chunks. It's now part of your Knowledge Journey.")
                else:
                    st.warning("File uploaded, but no readable text chunks were extracted.")
            except Exception as e:
                st.error(f"Error during indexing: {e}")
            finally:
                db.close()
