import logging
from huggingface_hub import InferenceClient
from app.core.config import settings

logger = logging.getLogger("financial_copilot")

# 🔹 Huggingface Inference API
HF_API_KEY = settings.HF_TOKEN
HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    # 🔹 Dimensión del modelo de embeddings
    dimension = 768

    @staticmethod
    def embed_text(text: str) -> list:
        """Generate embeddings using Huggingface Inference API"""
        try:
            logger.info(f"Generating embedding for text: {text[:50]}...")
            client = InferenceClient(api_key=HF_API_KEY)
            
            embedding = client.get_sentence_embeddings(
                model=HF_MODEL,
                inputs=text
            )
            
            logger.info(f"Embedding generated: dimension {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {repr(e)}")
            raise RuntimeError(f"Error generating embedding: {repr(e)}")
