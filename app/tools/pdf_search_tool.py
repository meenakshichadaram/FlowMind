from langchain_core.tools import tool
from app.rag.vector_store import vector_store_instance

@tool
def pdf_search_tool(query: str) -> str:
    """Searches indexed PDFs and lecture documents in the ChromaDB vector database for specific concepts or topics."""
    results = vector_store_instance.search_similar(query, top_k=3, filter_dict={"source_type": "PDF"})
    if not results:
        results = vector_store_instance.search_similar(query, top_k=3)

    if not results:
        return "No relevant PDF documents found for query."

    formatted = []
    for r in results:
        formatted.append(f"📄 [Source: {r.source_name} | Score: {r.score}]\n{r.content}")

    return "\n\n".join(formatted)
