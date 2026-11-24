import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.rag.embeddings import EmbeddingService
from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import DocumentChunker
from app.schemas.pydantic_models import DocumentChunk
from app.utils.logger import logger

class VectorStoreManager:
    """Manages ChromaDB vector indexing, semantic search, and document retrieval."""

    def __init__(self, collection_name: str = "student_workflow_knowledge"):
        self.embedding_service = EmbeddingService()
        self.embeddings = self.embedding_service.get_embeddings()
        
        # Initialize persistent Chroma client
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"ChromaDB initialized. Active collection: '{collection_name}' (Total items: {self.collection.count()})")

    def index_file(self, file_path: str) -> int:
        """Loads, chunks, embeds, and indexes a file into ChromaDB."""
        docs = DocumentLoader.load_auto(file_path)
        chunker = DocumentChunker()
        chunks = chunker.chunk_documents(docs)

        if not chunks:
            logger.warning(f"No text extracted from '{file_path}'. Skipping indexing.")
            return 0

        ids = [c["id"] + f"_{i}" for i, c in enumerate(chunks)]
        contents = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        
        # Generate embeddings
        vectors = self.embeddings.embed_documents(contents)

        self.collection.add(
            ids=ids,
            embeddings=vectors,
            documents=contents,
            metadatas=metadatas
        )
        logger.info(f"Indexed {len(chunks)} chunks into ChromaDB from '{file_path}'.")
        return len(chunks)

    def search_similar(self, query: str, top_k: int = 4, filter_dict: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Performs semantic search against ChromaDB."""
        if self.collection.count() == 0:
            logger.info("ChromaDB collection is empty.")
            return []

        query_vector = self.embeddings.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=filter_dict
        )

        retrieved_chunks = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc_text, meta, doc_id, dist in zip(docs, metas, ids, distances):
                score = round(1.0 - dist, 4) if dist <= 1.0 else round(dist, 4)
                retrieved_chunks.append(DocumentChunk(
                    doc_id=doc_id,
                    content=doc_text,
                    source_name=str(meta.get("source", "Unknown")),
                    source_type=str(meta.get("source_type", "Document")),
                    score=score,
                    metadata=meta
                ))

        logger.info(f"ChromaDB search for '{query}' returned {len(retrieved_chunks)} results.")
        return retrieved_chunks

    def seed_initial_knowledge(self):
        """Indexes initial student context into ChromaDB if empty."""
        if self.collection.count() > 0:
            return

        logger.info("Seeding initial knowledge base into ChromaDB...")
        sample_texts = [
            {
                "content": "Attention Is All You Need (Vaswani et al.): Introduces the Transformer architecture using self-attention mechanisms without recurrence. Multi-Head Attention allows joint attention to information from different representation subspaces.",
                "metadata": {"source": "Attention_Paper.pdf", "source_type": "PDF", "topic": "Deep Learning"}
            },
            {
                "content": "MIT 6.824 Lecture 5 (Raft Consensus): Raft achieves consensus by first electing a distinguished leader, then giving the leader complete responsibility for managing the replicated log. Leaders accept log entries from clients and replicate them on other servers.",
                "metadata": {"source": "MIT_6824_Raft.txt", "source_type": "Lecture Notes", "topic": "Distributed Systems"}
            },
            {
                "content": "LangGraph StateGraph Guide: LangGraph enables building multi-agent cyclic workflows. A StateGraph maintains explicit typed state across nodes, tool executions, and conditional edges.",
                "metadata": {"source": "LangGraph_Docs.md", "source_type": "Documentation", "topic": "AI Frameworks"}
            }
        ]

        ids = [f"seed_{i}" for i in range(len(sample_texts))]
        contents = [item["content"] for item in sample_texts]
        metadatas = [item["metadata"] for item in sample_texts]
        vectors = self.embeddings.embed_documents(contents)

        self.collection.add(ids=ids, embeddings=vectors, documents=contents, metadatas=metadatas)
        logger.info("ChromaDB seed knowledge successfully created.")

vector_store_instance = VectorStoreManager()
