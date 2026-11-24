from langchain_core.tools import tool
from app.config.llm_factory import LLMFactory

@tool
def summarizer_tool(text_to_summarize: str) -> str:
    """Summarizes lengthy study notes, articles, or lecture transcripts into structured bullet points."""
    llm = LLMFactory.get_llm(temperature=0.3)
    prompt = (
        f"Synthesize the following text into key takeaways, core concepts, and actionable study points:\n\n"
        f"{text_to_summarize[:3000]}"
    )
    res = llm.invoke(prompt)
    return str(res.content)
