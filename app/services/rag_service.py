from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.services.llm_service import LLMService
from app.services.pdf_service import PDFService
from app.utils.text_splitter import TextSplitter
from app.core.logger import setup_logger

logger = setup_logger()


class RAGService:

    vector_store = VectorStoreService()

    @staticmethod
    def process_document(file_path: str):
        text = PDFService.extract_text(file_path)
        chunks = TextSplitter.split_text(text)

        for chunk in chunks:
            emb = EmbeddingService.embed_text(chunk)
            RAGService.vector_store.add(emb, chunk)

    @staticmethod
    def ask(query: str):
        q_emb = EmbeddingService.embed_text(query)
        context_chunks = RAGService.vector_store.search(q_emb, k=3)

        if not context_chunks:
           return "No relevant information was found in the indexed documents."
    
        context = "\n\n".join(context_chunks)

        prompt = f"""
You are a financial AI assistant.

Use ONLY the following context to answer:

{context}

Question: {query}

If the answer is not in the context, say:
"I don't have enough information in the provided documents."
"""

        try:
            return LLMService.generate(prompt)
        except Exception as e:
            import traceback as tb_module
            tb = tb_module.format_exc()
            logger.error("LLM generation failed: %s\nTraceback:\n%s", repr(e), tb)
            logger.warning("Falling back to returning raw context chunks")
            # Fallback: return extracted context directly
            return f"Based on the indexed documents, here is relevant information:\n\n{context}"
