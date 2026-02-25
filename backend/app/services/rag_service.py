from app.services.embedding_service import EmbeddingService
from app.services.vector_service import get_vector_service
from app.services.llm_service import LLMService
from app.services.pdf_service import PDFService
from app.utils.text_splitter import TextSplitter
from app.core.logger import setup_logger

logger = setup_logger()


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Orchestrates document processing, vector search, and LLM generation.
    """

    @staticmethod
    def process_document(file_path: str, metadata: dict = None):
        """
        Process a PDF document: extract text, chunk, embed, and store.
        
        Args:
            file_path: Path to PDF file
            metadata: Optional metadata to attach (e.g., filename, upload date)
        """
        # Extract text from PDF
        text = PDFService.extract_text(file_path)
        
        # Split into chunks
        chunks = TextSplitter.split_text(text)
        
        # Prepare metadata for each chunk
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_meta = {
                "source": file_path,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            if metadata:
                chunk_meta.update(metadata)
            chunk_metadatas.append(chunk_meta)
        
        # Get vector service and add documents
        vector_service = get_vector_service()
        doc_ids = vector_service.add_documents(chunks, chunk_metadatas)
        
        logger.info(f"✅ Processed document: {len(chunks)} chunks, {len(doc_ids)} IDs")
        return doc_ids

    @staticmethod
    def ask(query: str) -> dict:
        """
        Answer a question using RAG pipeline.
        
        Args:
            query: User's question
        
        Returns:
            Dict with answer, model, chunks, and context
        """
        # Get vector service and search for relevant chunks
        vector_service = get_vector_service()
        search_results = vector_service.similarity_search(query, k=3)

        if not search_results:
            return {
                "answer": "No relevant information was found in the indexed documents.",
                "model": "none",
                "chunks": [],
                "context": ""
            }
        
        # Extract text content from search results
        context_chunks = [doc["content"] for doc in search_results]
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
            answer, model_used = LLMService.generate(prompt)
            return {
                "answer": answer,
                "model": model_used,
                "chunks": context_chunks,
                "context": context
            }
        except Exception as e:
            import traceback as tb_module
            tb = tb_module.format_exc()
            logger.error("LLM generation failed: %s\nTraceback:\n%s", repr(e), tb)
            logger.warning("Falling back to returning raw context chunks")
            # Fallback: return extracted context directly
            return {
                "answer": f"Based on the indexed documents, here is relevant information:\n\n{context}",
                "model": "fallback-context",
                "chunks": context_chunks,
                "context": context
            }
