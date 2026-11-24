from langchain_core.embeddings import Embeddings
from app.config.llm_factory import LLMFactory
from app.utils.logger import logger

class EmbeddingService:
    """Abstracted embedding service layer allowing seamless model swapping."""

    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self._embeddings_instance = None

    def get_embeddings(self) -> Embeddings:
        if self._embeddings_instance is None:
            logger.info(f"Loading embedding provider: {self.provider}")
            self._embeddings_instance = LLMFactory.get_embeddings()
        return self._embeddings_instance
