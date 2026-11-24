from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import shutil
from pathlib import Path
from app.database.session import get_db
from app.config.settings import settings
from app.schemas.pydantic_models import (
    WorkflowRequest, WorkflowResponse, IntentRecoveryResponse,
    DeadlinePredictionResponse, FocusAnalysisResponse, ConceptGraphResponse,
    UnfinishedActivitySchema, DeadlineTaskSchema, FocusSessionSchema
)
from app.services.intent_recovery import IntentRecoveryEngine
from app.services.deadline_intelligence import DeadlineIntelligenceEngine
from app.services.knowledge_fusion import KnowledgeFusionEngine
from app.services.focus_intelligence import FocusIntelligenceEngine
from app.graph.workflow import flowmind_graph
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1", tags=["FlowMind Intelligence API"])

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "online", "app": settings.APP_NAME, "version": "1.0.0"}

# --- Unified LangGraph Workflow Execution ---
@router.post("/workflow/run", response_model=WorkflowResponse)
def run_workflow(request: WorkflowRequest, db: Session = Depends(get_db)):
    """Executes the single unified LangGraph workflow across all engines."""
    initial_state = {
        "user_id": request.user_id,
        "query": request.query,
        "engine_hint": request.engine_hint,
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
        "memory_updates": {}
    }

    try:
        final_state = flowmind_graph.invoke(initial_state)
        return WorkflowResponse(
            query=request.query,
            intent_detected=final_state.get("intent_detected", "general"),
            response=final_state.get("final_response", "Workflow execution completed."),
            reasoning=final_state.get("reasoning", ""),
            retrieved_docs=final_state.get("retrieved_docs", []),
            tools_executed=final_state.get("tools_executed", []),
            memory_updates=final_state.get("memory_updates", {})
        )
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Module 1: Intent Recovery ---
@router.get("/intent/analyze", response_model=IntentRecoveryResponse)
def analyze_intent(user_id: int = 1, db: Session = Depends(get_db)):
    """Analyzes and prioritizes unfinished digital work."""
    engine = IntentRecoveryEngine(db)
    return engine.analyze_unfinished_work(user_id=user_id)

@router.post("/intent/add", response_model=UnfinishedActivitySchema)
def add_unfinished_activity(activity: UnfinishedActivitySchema, db: Session = Depends(get_db)):
    """Registers a new unfinished activity."""
    engine = IntentRecoveryEngine(db)
    return engine.register_new_unfinished_item(
        title=activity.title,
        source_type=activity.source_type,
        url_or_path=activity.url_or_path or "",
        progress=activity.progress_percent,
        reason=activity.importance_reason or "",
        action=activity.recommended_action or ""
    )

# --- Module 2: Deadline Intelligence ---
@router.get("/deadlines/predict/{task_id}", response_model=DeadlinePredictionResponse)
def predict_deadline_risk(task_id: int, db: Session = Depends(get_db)):
    """Evaluates task risk score and completion probability."""
    engine = DeadlineIntelligenceEngine(db)
    return engine.evaluate_task_risk(task_id=task_id)

@router.get("/deadlines/list", response_model=List[DeadlineTaskSchema])
def list_deadlines(user_id: int = 1, db: Session = Depends(get_db)):
    """Lists all upcoming deadlines with status."""
    engine = DeadlineIntelligenceEngine(db)
    return engine.get_all_deadlines(user_id=user_id)

# --- Module 3: Knowledge Fusion ---
@router.post("/knowledge/fuse")
def fuse_knowledge(query: str, top_k: int = 4, db: Session = Depends(get_db)):
    """Executes Knowledge Fusion RAG search and concept graph construction."""
    engine = KnowledgeFusionEngine(db)
    return engine.fuse_knowledge_query(query=query, top_k=top_k)

@router.post("/documents/upload")
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads and indexes a document (PDF, TXT, MD, HTML) into ChromaDB vector store."""
    upload_path = Path(settings.UPLOAD_DIR) / file.filename
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    engine = KnowledgeFusionEngine(db)
    chunk_count = engine.index_document(str(upload_path))
    
    return {
        "filename": file.filename,
        "saved_path": str(upload_path),
        "chunks_indexed": chunk_count,
        "message": f"Successfully indexed '{file.filename}' into ChromaDB knowledge base."
    }

# --- Module 4: Focus Intelligence ---
@router.get("/focus/analyze", response_model=FocusAnalysisResponse)
def analyze_focus(user_id: int = 1, db: Session = Depends(get_db)):
    """Analyzes focus patterns and recommends session length."""
    engine = FocusIntelligenceEngine(db)
    return engine.analyze_focus_patterns(user_id=user_id)

@router.post("/focus/log", response_model=FocusSessionSchema)
def log_focus_session(
    duration_mins: int = 45,
    distractions: int = 2,
    tab_switches: int = 12,
    triggers: str = "Tab switching",
    db: Session = Depends(get_db)
):
    """Logs a completed study session and updates metrics."""
    engine = FocusIntelligenceEngine(db)
    return engine.log_new_focus_session(
        duration_mins=duration_mins,
        distraction_count=distractions,
        tab_switches=tab_switches,
        triggers=triggers
    )
