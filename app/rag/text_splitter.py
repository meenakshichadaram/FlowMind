from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.logger import logger

class DocumentChunker:
    """Splits loaded raw documents into optimal chunks for ChromaDB indexing."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_counter = 0

        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            raw_chunks = self.splitter.split_text(content)
            for idx, text_chunk in enumerate(raw_chunks):
                chunk_counter += 1
                chunk_meta = metadata.copy()
                chunk_meta["chunk_id"] = f"{metadata.get('source', 'doc')}_c{idx}"
                chunk_meta["chunk_index"] = idx
                
                chunks.append({
                    "id": f"chunk_{chunk_counter}",
                    "content": text_chunk,
                    "metadata": chunk_meta
                })

        logger.info(f"Chunked {len(documents)} documents into {len(chunks)} text chunks.")
        return chunks
