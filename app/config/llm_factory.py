from typing import Optional, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from app.config.settings import settings
from app.utils.logger import logger

class FallbackMockChatModel(BaseChatModel):
    """Fallback LLM model when no OpenAI API key is configured."""
    model_name: str = "fallback-mock"

    @property
    def _llm_type(self) -> str:
        return "fallback-mock"

    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None, **kwargs: Any) -> ChatResult:
        last_msg = messages[-1].content if messages else "No query provided"
        text_content = str(last_msg)
        
        reply = (
            f"[FlowMind Mock AI Response]\n\n"
            f"Processed workflow request: '{text_content[:150]}...'\n\n"
            f"• Analysis: Identified active student workflow items & memory metrics.\n"
            f"• Recommendation: Review high-risk deadlines and resume your top prioritized unfinished activity."
        )
        message = AIMessage(content=reply)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

class LLMFactory:
    """Centralized LLM and Embedding Factory for FlowMind AI."""
    
    @staticmethod
    def get_llm(temperature: float = 0.2, model_name: Optional[str] = None) -> BaseChatModel:
        model = model_name or settings.OPENAI_MODEL
        api_key = settings.OPENAI_API_KEY.strip()
        
        if api_key and api_key != "your_openai_api_key_here":
            try:
                logger.info(f"Initializing ChatOpenAI with model: {model}")
                return ChatOpenAI(
                    model=model,
                    temperature=temperature,
                    api_key=api_key
                )
            except Exception as e:
                logger.warning(f"Failed to initialize ChatOpenAI ({e}). Falling back to Mock LLM.")
        
        logger.info("Using Fallback Mock ChatModel (OpenAI API key not set or invalid).")
        return FallbackMockChatModel()

    @staticmethod
    def get_embeddings() -> Embeddings:
        api_key = settings.OPENAI_API_KEY.strip()
        
        if api_key and api_key != "your_openai_api_key_here":
            try:
                logger.info(f"Initializing OpenAIEmbeddings with model: {settings.OPENAI_EMBEDDING_MODEL}")
                return OpenAIEmbeddings(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    api_key=api_key
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAIEmbeddings ({e}). Falling back to Local Deterministic Embeddings.")
                
        # Abstracted fallback embedding model
        return MockEmbeddingProvider()

class MockEmbeddingProvider(Embeddings):
    """Abstracted deterministic local embedding generator for offline development."""
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._hash_text(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._hash_text(text)

    def _hash_text(self, text: str) -> list[float]:
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Produce a fixed length normalized vector of dimension 384
        raw = [float(b) / 255.0 for b in h]
        repeated = (raw * 12)[:384]
        norm = sum(x*x for x in repeated) ** 0.5 or 1.0
        return [x / norm for x in repeated]
