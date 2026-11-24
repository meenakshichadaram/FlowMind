import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.config.settings import settings
from app.ui.theme import inject_theme

st.set_page_config(page_title="Settings - FlowMind AI", page_icon="⚙️", layout="wide")
inject_theme()

st.markdown('<div class="fm-greeting">Settings</div>', unsafe_allow_html=True)
st.markdown('<div class="fm-subtitle">Environment configuration and diagnostics.</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="fm-section-title">🧠 AI Model Configuration</div>', unsafe_allow_html=True)
    api_key_set = bool(settings.OPENAI_API_KEY.strip()) and settings.OPENAI_API_KEY != "your_openai_api_key_here"
    st.markdown(
        f"""
        <div class="fm-card">
            • <b>OpenAI API Key</b>: {'✅ Configured' if api_key_set else '⚠️ Not set (using fallback mock LLM)'}<br>
            • <b>LLM Model</b>: <code>{settings.OPENAI_MODEL}</code><br>
            • <b>Embedding Model</b>: <code>{settings.OPENAI_EMBEDDING_MODEL}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown('<div class="fm-section-title">💾 Database & Vector Storage</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="fm-card">
            • <b>SQLite DB</b>: <code>{settings.DATABASE_URL}</code><br>
            • <b>ChromaDB Directory</b>: <code>{settings.CHROMA_PERSIST_DIR}</code><br>
            • <b>Upload Directory</b>: <code>{settings.UPLOAD_DIR}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="fm-section-title">🔍 OCR Diagnostics</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="fm-card">Tesseract Command Path: <code>{settings.TESSERACT_CMD or "Default System PATH"}</code></div>',
    unsafe_allow_html=True,
)
try:
    import pytesseract
    st.success("✅ `pytesseract` library imported successfully.")
except Exception as e:
    st.warning(f"⚠️ pytesseract import warning: {e}")
