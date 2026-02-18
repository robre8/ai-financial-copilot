import logging
import gc
import numpy as np
from huggingface_hub import InferenceClient
from app.core.config import settings

logger = logging.getLogger("financial_copilot")

# 🔹 Huggingface Inference API
HF_API_KEY = settings.HF_TOKEN
HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    # 🔹 Dimensión del modelo de embeddings (all-MiniLM-L6-v2 = 384)
    dimension = 384

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
            
            # 🔹 Normalize to 1D array: feature_extraction can return nested arrays
            embedding = np.array(embedding)
            while embedding.ndim > 1:
                # If 2D or 3D (e.g., [[0.1, 0.2, ...]] or [[[...]]]), take mean pooling
                embedding = embedding.mean(axis=0)
            
            embedding = embedding.flatten().tolist()
            
            # 🔹 Validate dimension
            if len(embedding) != EmbeddingService.dimension:
                raise ValueError(
                    f"Expected {EmbeddingService.dimension}-dim embedding, "
                    f"got {len(embedding)}-dim"
                )
            
            # 🔹 Memory cleanup
            del client
            gc.collect()
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {repr(e)}")
            raise RuntimeError(f"Error generating embedding: {repr(e)}")
