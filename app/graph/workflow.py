from langgraph.graph import StateGraph, END
from app.graph.state import WorkflowState
from app.graph.nodes import (
    input_node,
    intent_classification_node,
    memory_retrieval_node,
    rag_retrieval_node,
    tool_execution_node,
    reasoning_node,
    memory_update_node,
    generate_response_node
)
from app.utils.logger import logger

def route_rag(state: WorkflowState) -> str:
    """Conditional router for RAG Retrieval step."""
    if state.get("need_rag"):
        return "rag_retrieval"
    return "check_tool"

def route_tool(state: WorkflowState) -> str:
    """Conditional router for Tool Execution step."""
    if state.get("need_tool"):
        return "tool_execution"
    return "reasoning"

def build_flowmind_graph():
    """Assembles and compiles the FlowMind LangGraph Workflow Graph."""
    workflow = StateGraph(WorkflowState)

    # 1. Add Nodes
    workflow.add_node("input", input_node)
    workflow.add_node("intent_classification", intent_classification_node)
    workflow.add_node("memory_retrieval", memory_retrieval_node)
    workflow.add_node("rag_retrieval", rag_retrieval_node)
    workflow.add_node("tool_execution", tool_execution_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("memory_update", memory_update_node)
    workflow.add_node("generate_response", generate_response_node)

    # 2. Add Edges & Conditional Routing
    workflow.set_entry_point("input")
    workflow.add_edge("input", "intent_classification")
    workflow.add_edge("intent_classification", "memory_retrieval")

    # Conditional Branch: Need RAG?
    workflow.add_conditional_edges(
        "memory_retrieval",
        route_rag,
        {
            "rag_retrieval": "rag_retrieval",
            "check_tool": "tool_execution"  # Route directly to tool check if no RAG
        }
    )

    # From RAG -> Check Tool
    workflow.add_conditional_edges(
        "rag_retrieval",
        route_tool,
        {
            "tool_execution": "tool_execution",
            "reasoning": "reasoning"
        }
    )

    # From Tool Execution -> Reasoning
    workflow.add_edge("tool_execution", "reasoning")

    # Reasoning -> Memory Update -> Generate Response -> END
    workflow.add_edge("reasoning", "memory_update")
    workflow.add_edge("memory_update", "generate_response")
    workflow.add_edge("generate_response", END)

    app_graph = workflow.compile()
    logger.info("FlowMind LangGraph workflow successfully assembled and compiled.")
    return app_graph

flowmind_graph = build_flowmind_graph()
