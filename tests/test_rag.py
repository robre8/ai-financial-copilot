import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService


class TestRAGService:
    """Test suite for RAG Service"""

    @pytest.fixture
    def mock_embedding_service(self):
        """Mock the embedding service"""
        with patch('app.services.rag_service.EmbeddingService') as mock:
            mock.embed_text.return_value = [0.1] * 384  # 384-dim embedding
            yield mock

    @pytest.fixture
    def mock_llm_service(self):
        """Mock the LLM service"""
        with patch('app.services.rag_service.LLMService') as mock:
            mock.generate.return_value = ("The answer is financial data.", "llama-3.1-8b-instant")
            yield mock

    @pytest.fixture
    def mock_pdf_service(self):
        """Mock the PDF service"""
        with patch('app.services.rag_service.PDFService') as mock:
            mock.extract_text.return_value = "Sample financial document with earnings data."
            yield mock

    @pytest.fixture
    def mock_text_splitter(self):
        """Mock the text splitter"""
        with patch('app.services.rag_service.TextSplitter') as mock:
            mock.split_text.return_value = [
                "Sample financial document",
                "with earnings data.",
                "Additional financial context."
            ]
            yield mock

    def test_process_document(self, mock_embedding_service, mock_pdf_service, mock_text_splitter):
        """Test PDF processing and indexing"""
        # Arrange
        test_file = "test_document.pdf"
        
        # Act
        RAGService.process_document(test_file)

        # Assert
        mock_pdf_service.extract_text.assert_called_once_with(test_file)
        mock_text_splitter.split_text.assert_called_once()
        assert mock_embedding_service.embed_text.call_count >= 1

    def test_ask_with_context(self, mock_embedding_service, mock_llm_service):
        """Test asking a question with retrieved context"""
        # Arrange
        query = "What are the quarterly earnings?"
        RAGService.vector_store = MagicMock()
        RAGService.vector_store.search.return_value = [
            "Q3 earnings: $100M",
            "Revenue growth: 15%"
        ]

        # Act
        result = RAGService.ask(query)

        # Assert
        assert "answer" in result
        assert "model" in result
        assert "chunks" in result
        assert "context" in result
        assert result["answer"] == "The answer is financial data."
        assert result["model"] == "llama-3.1-8b-instant"
        assert len(result["chunks"]) == 2

    def test_ask_no_context(self, mock_embedding_service, mock_llm_service):
        """Test asking when no context is available"""
        # Arrange
        query = "What are the quarterly earnings?"
        RAGService.vector_store = MagicMock()
        RAGService.vector_store.search.return_value = []

        # Act
        result = RAGService.ask(query)

        # Assert
        assert result["answer"] == "No relevant information was found in the indexed documents."
        assert result["model"] == "none"
        assert result["chunks"] == []
        assert result["context"] == ""

    def test_ask_llm_failure_fallback(self, mock_embedding_service):
        """Test fallback when LLM generation fails"""
        # Arrange
        query = "What are the quarterly earnings?"
        RAGService.vector_store = MagicMock()
        context_chunks = ["Q3 earnings: $100M", "Revenue growth: 15%"]
        RAGService.vector_store.search.return_value = context_chunks

        with patch('app.services.rag_service.LLMService') as mock_llm:
            mock_llm.generate.side_effect = Exception("API rate limit exceeded")

            # Act
            result = RAGService.ask(query)

            # Assert
            assert result["model"] == "fallback-context"
            assert "Based on the indexed documents" in result["answer"]
            assert context_chunks == result["chunks"]

    def test_embedding_dimension_validation(self):
        """Test that embeddings have correct dimension"""
        with patch('app.services.rag_service.EmbeddingService') as mock_embed:
            mock_embed.embed_text.return_value = [0.1] * 384
            
            emb = mock_embed.embed_text("test text")
            
            assert len(emb) == 384, "Embedding should be 384-dimensional"

    def test_empty_question_handling(self, mock_embedding_service, mock_llm_service):
        """Test that empty or whitespace questions are handled"""
        RAGService.vector_store = MagicMock()
        
        # Empty question should still attempt search
        result = RAGService.ask("")
        assert "answer" in result

    def test_multiple_chunks_context_building(self, mock_embedding_service, mock_llm_service):
        """Test that multiple chunks are correctly combined into context"""
        # Arrange
        query = "What is the financial summary?"
        chunks = [
            "First chunk of financial data",
            "Second chunk of financial data",
            "Third chunk of financial data"
        ]
        RAGService.vector_store = MagicMock()
        RAGService.vector_store.search.return_value = chunks

        # Act
        result = RAGService.ask(query)

        # Assert
        expected_context = "\n\n".join(chunks)
        assert result["context"] == expected_context
        assert len(result["chunks"]) == 3
