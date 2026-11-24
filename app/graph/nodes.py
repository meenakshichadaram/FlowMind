from typing import Dict, Any
from app.graph.state import WorkflowState
from app.database.session import SessionLocal
from app.memory.memory_manager import MemoryManager
from app.rag.vector_store import vector_store_instance
from app.config.llm_factory import LLMFactory
from app.tools.pdf_search_tool import pdf_search_tool
from app.tools.summarizer_tool import summarizer_tool
from app.tools.task_breakdown_tool import task_breakdown_tool
from app.tools.calendar_tool import calendar_tool
from app.tools.deadline_risk_tool import deadline_risk_tool
from app.tools.focus_score_tool import focus_score_tool
from app.tools.knowledge_graph_tool import knowledge_graph_tool
from app.tools.file_search_tool import file_search_tool
from app.utils.logger import logger

def input_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 1: Receives and normalizes user query state."""
    logger.info(f"[LangGraph Node 1: Input] Query: '{state['query']}'")
    return {
        "query": state["query"].strip(),
        "user_id": state.get("user_id", 1),
        "tools_executed": [],
        "retrieved_docs": []
    }

def intent_classification_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 2: Classifies query intent and determines RAG / Tool execution flags."""
    query = state["query"].lower()
    hint = (state.get("engine_hint") or "").lower()

    if hint in ["intent", "intent_recovery"] or any(k in query for k in ["unfinished", "resume", "pending", "incomplete", "abandoned"]):
        intent = "intent_recovery"
        need_rag = False
        need_tool = True
        tool_name = "file_search_tool"
    elif hint in ["deadline", "deadline_intelligence"] or any(k in query for k in ["deadline", "due", "schedule", "risk", "probability", "finish"]):
        intent = "deadline_intelligence"
        need_rag = False
        need_tool = True
        tool_name = "deadline_risk_tool"
    elif hint in ["fusion", "knowledge_fusion"] or any(k in query for k in ["concept", "paper", "rag", "search", "pdf", "explain", "graph", "link"]):
        intent = "knowledge_fusion"
        need_rag = True
        need_tool = True
        tool_name = "pdf_search_tool"
    elif hint in ["focus", "focus_intelligence"] or any(k in query for k in ["focus", "distraction", "pomodoro", "score", "fatigue", "session"]):
        intent = "focus_intelligence"
        need_rag = False
        need_tool = True
        tool_name = "focus_score_tool"
    else:
        intent = "general_workflow"
        need_rag = True
        need_tool = False
        tool_name = None

    logger.info(f"[LangGraph Node 2: Intent Classification] Classified as '{intent}' (Need RAG: {need_rag}, Need Tool: {need_tool})")
    return {
        "intent_detected": intent,
        "need_rag": need_rag,
        "need_tool": need_tool,
        "tool_to_execute": tool_name
    }

def memory_retrieval_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 3: Fetches structured long-term memory from SQLite."""
    db = SessionLocal()
    try:
        mem = MemoryManager(db)
        snapshot = mem.get_full_student_memory_snapshot(user_id=state["user_id"])
        logger.info(f"[LangGraph Node 3: Memory Retrieval] Memory snapshot retrieved for user {state['user_id']}")
        return {"memory_snapshot": snapshot}
    finally:
        db.close()

def rag_retrieval_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 4: Retrieves vector embeddings and text chunks from ChromaDB."""
    if not state.get("need_rag"):
        return {"retrieved_docs": []}

    logger.info(f"[LangGraph Node 4: Document Retrieval] Querying ChromaDB for '{state['query']}'")
    chunks = vector_store_instance.search_similar(query=state["query"], top_k=3)
    return {"retrieved_docs": chunks}

def tool_execution_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 5: Executes LangChain tools if required by workflow intent."""
    if not state.get("need_tool") or not state.get("tool_to_execute"):
        return {"tool_execution_result": None}

    tool_name = state["tool_to_execute"]
    logger.info(f"[LangGraph Node 5: Tool Execution] Executing tool '{tool_name}'")
    
    result_str = ""
    try:
        if tool_name == "pdf_search_tool":
            result_str = pdf_search_tool.invoke({"query": state["query"]})
        elif tool_name == "deadline_risk_tool":
            result_str = deadline_risk_tool.invoke({"hours_remaining": 6.0, "days_left": 3.0, "complexity": 4, "completion_rate": 0.85})
        elif tool_name == "focus_score_tool":
            result_str = focus_score_tool.invoke({"duration_mins": 50, "distractions": 2, "tab_switches": 12})
        elif tool_name == "file_search_tool":
            result_str = file_search_tool.invoke({"file_keyword": state["query"]})
        elif tool_name == "knowledge_graph_tool":
            result_str = knowledge_graph_tool.invoke({"topic": state["query"]})
        else:
            result_str = f"Tool '{tool_name}' executed."
    except Exception as e:
        logger.error(f"Error executing tool '{tool_name}': {e}")
        result_str = f"Tool execution notice: {e}"

    executed = list(state.get("tools_executed", []))
    executed.append(tool_name)

    return {
        "tool_execution_result": str(result_str),
        "tools_executed": executed
    }

def reasoning_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 6: Synthesizes final response using LLM multi-step reasoning."""
    llm = LLMFactory.get_llm(temperature=0.3)
    intent = state.get("intent_detected", "general")
    query = state.get("query", "")
    mem = state.get("memory_snapshot", {})
    docs = state.get("retrieved_docs", [])
    tool_res = state.get("tool_execution_result", "")

    doc_str = "\n".join([f"• [{d.source_name}]: {d.content[:300]}" for d in docs]) if docs else "None"
    
    prompt = (
        f"You are FlowMind AI - Intelligent Student Workflow Intelligence Platform.\n"
        f"Intent Detected: {intent.upper()}\n"
        f"User Query: '{query}'\n\n"
        f"Memory Context:\n{mem}\n\n"
        f"RAG Retrieved Documents:\n{doc_str}\n\n"
        f"Tool Output:\n{tool_res}\n\n"
        f"Provide a structured, highly actionable workflow intelligence response."
    )

    reasoning_reply = llm.invoke(prompt).content
    logger.info(f"[LangGraph Node 6: Reasoning] Generated reasoning response.")
    return {
        "reasoning": f"Synthesized workflow insight for {intent} with {len(docs)} retrieved RAG chunks and tool result.",
        "final_response": str(reasoning_reply)
    }

def memory_update_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 7: Updates SQLite structured memory with session activity."""
    logger.info(f"[LangGraph Node 7: Memory Update] Logging workflow activity.")
    return {
        "memory_updates": {
            "query_logged": state["query"],
            "intent": state["intent_detected"],
            "timestamp": "now"
        }
    }

def generate_response_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 8: Final return node."""
    logger.info(f"[LangGraph Node 8: Generate Response] Workflow completed.")
    return {}
