import logging
import gc
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
            # 🔹 Correct parameter name is 'token', not 'api_key'
            client = InferenceClient(token=HF_API_KEY)
            
            embedding = client.feature_extraction(
                text=text,
                model=HF_MODEL
            )
            
            # 🔹 Memory cleanup
            del client
            gc.collect()
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {repr(e)}")
            raise RuntimeError(f"Error generating embedding: {repr(e)}")
