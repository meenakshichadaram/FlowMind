from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.memory.memory_manager import MemoryManager

@tool
def knowledge_graph_tool(topic: str) -> str:
    """Generates concept relations and revision path for a given learning topic across course materials."""
    db = SessionLocal()
    try:
        mem = MemoryManager(db)
        links = mem.get_concept_links()
        
        filtered = [
            f"• {link.source_concept} --[{link.relationship_type}]--> {link.target_concept} (Ref: {link.resource_ref})"
            for link in links
            if topic.lower() in link.source_concept.lower() or topic.lower() in link.target_concept.lower() or topic.lower() in link.relationship_type.lower() or topic == "all"
        ]

        if not filtered:
            return f"No direct graph links found for '{topic}'. Showing foundational concepts:\n" + "\n".join([
                f"• {link.source_concept} --> {link.target_concept}" for link in links[:3]
            ])

        return f"🕸 Knowledge Graph Relations for '{topic}':\n" + "\n".join(filtered)
    finally:
        db.close()
