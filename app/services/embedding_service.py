from huggingface_hub import InferenceClient
from app.core.config import settings
import numpy as np


class EmbeddingService:

    # 🔹 Dimensión del modelo
    dimension = 384
    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

    @staticmethod
    def embed_text(text: str):
        """Generate embeddings using Huggingface Inference API"""
        try:
            # Use the official InferenceClient for feature extraction
            response = EmbeddingService.client.feature_extraction(
                text,
                model=EmbeddingService.model_name,
            )
            
            # Convert numpy array to list if needed
            if isinstance(response, np.ndarray):
                response = response.tolist()
            
            # Response should be a list of floats (embedding vector)
            
            raise ValueError(f"Unexpected embedding response format: {type(response)}")
            
        except Exception as e:
            raise RuntimeError(f"Error generating embedding: {str(e)}")
