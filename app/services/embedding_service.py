import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("financial_copilot")


class EmbeddingService:
    # 🔹 Lazy-load model to avoid unnecessary initialization
    model = None
    
    # 🔹 Dimensión del modelo
    dimension = 384

    @classmethod
    def get_model(cls):
        """Load embedding model on first use (lazy initialization)"""
        if cls.model is None:
            logger.info("Loading embedding model (all-MiniLM-L6-v2)...")
            cls.model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        return cls.model

    @staticmethod
    def embed_text(text: str) -> list:
        """Generate embeddings locally using sentence-transformers"""
        try:
            model = EmbeddingService.get_model()
            embedding = model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {repr(e)}")
            raise RuntimeError(f"Error generating embedding: {repr(e)}")
