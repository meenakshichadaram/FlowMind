from app.rag.text_splitter import DocumentChunker
from app.rag.embeddings import EmbeddingService

def test_chunker_and_embeddings():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    sample_doc = [{
        "content": "FlowMind AI is a student workflow intelligence platform. It observes, predicts, and retrieves workflow state.",
        "metadata": {"source": "test_doc.txt"}
    }]
    chunks = chunker.chunk_documents(sample_doc)
    assert len(chunks) >= 1
    assert "chunk_id" in chunks[0]["metadata"]

    embeddings = EmbeddingService().get_embeddings()
    vecs = embeddings.embed_documents(["FlowMind AI test sentence"])
    assert len(vecs) == 1
    assert len(vecs[0]) > 0
