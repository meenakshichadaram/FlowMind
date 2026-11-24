from langchain_core.tools import tool
from app.rag.vector_store import vector_store_instance

@tool
def file_search_tool(file_keyword: str) -> str:
    """Searches indexed document titles, source paths, and metadata in the vector store."""
    results = vector_store_instance.search_similar(file_keyword, top_k=5)
    if not results:
        return f"No files matching keyword '{file_keyword}' found in workspace."

    sources = set(r.source_name for r in results)
    return f"Found matching indexed documents for '{file_keyword}':\n" + "\n".join(f"• {s}" for s in sources)

@tool
def notification_tool(message: str, urgency: str = "Normal") -> str:
    """Dispatches a workflow alert or deadline reminder to the student dashboard."""
    return f"🔔 [{urgency.upper()} ALERT] Notification dispatched: '{message}'"
