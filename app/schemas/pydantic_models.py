from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# --- User Profile Schemas ---
class UserProfileSchema(BaseModel):
    id: int
    name: str
    email: str
    preferred_work_hours: str
    avg_study_session_mins: int
    daily_goal_hours: float

    class Config:
        from_attributes = True

# --- Intent Recovery Schemas ---
class UnfinishedActivitySchema(BaseModel):
    id: Optional[int] = None
    user_id: int = 1
    title: str
    source_type: str  # PDF, Video, Article, App, Code, Note
    url_or_path: Optional[str] = None
    progress_percent: float = 0.0
    priority_score: float = 50.0
    revisit_count: int = 0
    importance_reason: Optional[str] = None
    recommended_action: Optional[str] = None
    last_accessed: Optional[datetime] = None

    class Config:
        from_attributes = True

class IntentRecoveryResponse(BaseModel):
    unfinished_count: int
    top_priorities: List[UnfinishedActivitySchema]
    workflow_summary: str
    recommended_next_step: str

# --- Deadline Intelligence Schemas ---
class DeadlineTaskSchema(BaseModel):
    id: Optional[int] = None
    user_id: int = 1
    title: str
    course_or_project: str
    due_date: datetime
    estimated_hours_remaining: float
    complexity_level: int = 3
    historical_completion_rate: float = 0.85
    completion_probability: float = 0.75
    risk_score: float = 25.0
    status: str = "Pending"

    class Config:
        from_attributes = True

class DeadlinePredictionResponse(BaseModel):
    task_title: str
    completion_probability: float
    predicted_finish_date: str
    risk_score: float
    risk_level: str  # Low, Moderate, High, Critical
    recommended_schedule: List[Dict[str, Any]]
    explanation: str

# --- Knowledge Fusion Schemas ---
class DocumentChunk(BaseModel):
    doc_id: str
    content: str
    source_name: str
    source_type: str
    score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConceptNode(BaseModel):
    id: str
    label: str
    category: str = "concept"

class ConceptEdge(BaseModel):
    source: str
    target: str
    relationship: str
    strength: float = 1.0

class ConceptGraphResponse(BaseModel):
    nodes: List[ConceptNode]
    edges: List[ConceptEdge]
    revision_path: List[str]
    summary: str

# --- Focus Intelligence Schemas ---
class FocusSessionSchema(BaseModel):
    id: Optional[int] = None
    user_id: int = 1
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_mins: int = 0
    distraction_count: int = 0
    tab_switch_count: int = 0
    focus_score: float = 85.0
    distraction_triggers: str = "None"

    class Config:
        from_attributes = True

class FocusAnalysisResponse(BaseModel):
    current_focus_score: float
    productivity_state: str  # Peak, Normal, Distracted, Exhausted
    distraction_risks: List[str]
    recommended_session_mins: int
    optimal_break_mins: int
    actionable_insights: List[str]

# --- Unified Workflow Payload Schemas ---
class WorkflowRequest(BaseModel):
    query: str
    user_id: int = 1
    engine_hint: Optional[str] = None  # intent, deadline, fusion, focus, or auto
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowResponse(BaseModel):
    query: str
    intent_detected: str
    response: str
    reasoning: str
    retrieved_docs: List[DocumentChunk] = Field(default_factory=list)
    tools_executed: List[str] = Field(default_factory=list)
    memory_updates: Dict[str, Any] = Field(default_factory=dict)
