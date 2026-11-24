# FlowMind AI – Your AI Operating System for Learning

**FlowMind AI** doesn't feel like four dashboards bolted together. It feels like one intelligent assistant that continuously watches your unfinished work, deadlines, knowledge base, and focus patterns, and answers one question every time you open it:

> "What is the most important thing I should do right now, based on everything you know about my learning journey?"

Internally, FlowMind is still powered by four specialized AI services orchestrated by a unified **LangGraph State Graph** — but externally, the student only ever talks to one assistant.

---

## 🌟 What FlowMind Does

### Home — the Intelligence Center
Opens with a plain-language read of today's situation ("your internship application closes in 18 hours," "you're 40 minutes from finishing your AI project"), then surfaces one **Recommended Next Action** with a clear reason and time estimate — not a wall of cards and stats.

### 🔁 Recovered Intentions *(internally: Intent Recovery Service)*
Surfaces abandoned PDFs, half-watched lectures, and unfinished code as a visual timeline — what you started, when you drifted, and the fastest way back in.

### 📡 Deadline Radar *(internally: Deadline Intelligence Service)*
Not reminders — predictions. Estimates whether you'll realistically finish before each deadline, with a risk score, completion probability, and a day-by-day suggested plan.

### 🗺️ Knowledge Journey *(internally: Knowledge Fusion Service)*
An interactive concept explorer, not a document search box. Pick a topic and see related concepts, prerequisites, your own notes, and the recommended next thing to learn.

### 📈 Productivity Insights *(internally: Focus Intelligence Service)*
Your focus patterns explained in plain language — when you're sharpest, what derails you, how your sessions compare across the week — generated dynamically from your real session data.

FlowMind is proactive, not reactive: every screen carries a recommendation, and every recommendation explains *why*. Memory is visible throughout — FlowMind references what you did yesterday, what you've revisited, and what it's still watching closely.

---

## 🏗 System Architecture & Tech Stack

- **Backend**: Python 3.13, FastAPI, Uvicorn
- **Orchestration**: LangGraph, LangChain (State Graph pattern with custom tools) + a lightweight fusion `IntelligenceOrchestrator` that combines all four services for the unified product experience
- **Structured Memory**: SQLite with SQLAlchemy ORM
- **Vector Database**: ChromaDB with abstract embedding provider layer (OpenAI Embeddings with local mock fallback)
- **Document Processing**: PyMuPDF (`fitz`), BeautifulSoup4, Unstructured, PyTesseract OCR
- **Frontend**: Streamlit, dark, premium, card/timeline-based product UI (no admin-dashboard styling)

---

## 🚀 Quick Start Guide

### 1. Setup Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and add your OpenAI API Key (Optional for live LLM mode; mock fallback works out-of-the-box):
```bash
cp .env.example .env
```

### 4. Initialize Database & Seed Data
```bash
python -m app.database.session
```

### 5. Launch FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8000
```
- API Docs available at: `http://127.0.0.1:8000/docs`

### 6. Launch Streamlit UI Dashboard
```bash
streamlit run app/ui/streamlit_app.py
```
- Open your browser at: `http://localhost:8501`

---

## 📂 Project Structure

```
flowmind_ai/
├── app/
│   ├── api/             # FastAPI REST endpoints
│   ├── config/          # Centralized LLM & App Settings
│   ├── database/        # SQLite Models & Database Session Engine
│   ├── graph/           # LangGraph State, Nodes & Workflow Assembly
│   ├── memory/          # SQLite Structured Long-Term Memory CRUD
│   ├── rag/             # Document Processing & ChromaDB Vector Store
│   ├── schemas/         # Pydantic Request/Response Data Models
│   ├── services/        # 4 Core AI Engines (Intent, Deadline, Fusion, Focus)
│   ├── tools/           # Modular LangChain Custom Tools
│   ├── ui/              # Streamlit Multi-page Dark UI Dashboard
│   └── utils/           # OCR and Logging Utilities
├── data/
│   ├── chroma/          # Persistent ChromaDB Directory
│   ├── uploads/         # User uploaded documents
│   └── sqlite.db        # SQLite DB file
└── tests/               # Suite of unit & integration tests
```

---

## 🔒 License & Credits
Built for modern AI workflow intelligence applications following modern LangChain & LangGraph best practices.
