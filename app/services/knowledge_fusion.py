from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.rag.vector_store import vector_store_instance
from app.memory.memory_manager import MemoryManager
from app.schemas.pydantic_models import ConceptGraphResponse, ConceptNode, ConceptEdge, DocumentChunk
from app.config.llm_factory import LLMFactory
from app.utils.logger import logger

class KnowledgeFusionEngine:
    """MODULE 3: Knowledge Fusion Engine
    Builds meaningful connections across learning resources using RAG (ChromaDB) and graph concept relations.
    """

    def __init__(self, db_session: Session):
        self.memory = MemoryManager(db_session)
        self.vector_store = vector_store_instance
        self.llm = LLMFactory.get_llm(temperature=0.3)

    def fuse_knowledge_query(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """Runs RAG vector retrieval and constructs semantic conceptual linkages."""
        # 1. Semantic Search in ChromaDB
        chunks: List[DocumentChunk] = self.vector_store.search_similar(query, top_k=top_k)
        
        context_str = "\n\n".join([f"[Source: {c.source_name}]: {c.content}" for c in chunks])
        if not context_str:
            context_str = "No specific indexed chunks found for query."

        # 2. Extract concepts and relations via LLM
        prompt = (
            f"You are the Knowledge Fusion Engine for FlowMind AI.\n"
            f"Query: '{query}'\n\n"
            f"Context Documents:\n{context_str}\n\n"
            f"Provide:\n"
            f"1. Key Concept Connections across these sources\n"
            f"2. Recommended Revision Pathway (Step 1 -> Step 2 -> Step 3)\n"
            f"3. Synthesis explanation."
        )
        synthesis = str(self.llm.invoke(prompt).content)

        # 3. Retrieve Concept Graph from Memory
        db_links = self.memory.get_concept_links()
        nodes_dict = {}
        edges = []

        for link in db_links:
            src = link.source_concept
            tgt = link.target_concept
            nodes_dict[src] = ConceptNode(id=src, label=src, category="foundational" if link.relationship_type=="prerequisite" else "advanced")
            nodes_dict[tgt] = ConceptNode(id=tgt, label=tgt, category="applied")
            edges.append(ConceptEdge(
                source=src,
                target=tgt,
                relationship=link.relationship_type,
                strength=link.strength
            ))

        nodes = list(nodes_dict.values())
        revision_path = [n.label for n in nodes[:4]] if nodes else ["Foundation Concepts", "Core Theory", "Application"]

        graph_response = ConceptGraphResponse(
            nodes=nodes,
            edges=edges,
            revision_path=revision_path,
            summary=synthesis
        )

        return {
            "query": query,
            "retrieved_chunks": chunks,
            "graph": graph_response,
            "synthesis": synthesis
        }

    def index_document(self, file_path: str) -> int:
        """Indexes file into ChromaDB for Knowledge Fusion RAG."""
        return self.vector_store.index_file(file_path)
