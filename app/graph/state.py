from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.pydantic_models import DocumentChunk

class WorkflowState(TypedDict):
    """LangGraph State maintaining typed context across node steps."""
    user_id: int
    query: str
    engine_hint: Optional[str]
    intent_detected: str                # 'intent_recovery', 'deadline_intelligence', 'knowledge_fusion', 'focus_intelligence', or 'general'
    memory_snapshot: Dict[str, Any]
    need_rag: bool
    retrieved_docs: List[DocumentChunk]
    need_tool: bool
    tool_to_execute: Optional[str]
    tool_input_args: Dict[str, Any]
    tool_execution_result: Optional[str]
    tools_executed: List[str]
    reasoning: str
    final_response: str
    memory_updates: Dict[str, Any]
