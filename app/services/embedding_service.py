from huggingface_hub import InferenceClient
from app.core.config import settings
import numpy as np


class EmbeddingService:

    # 🔹 Dimensión del modelo
    dimension = 384
    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    client = InferenceClient(
        api_key=settings.HF_TOKEN,
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
            
            # Handle list format from Huggingface
            if isinstance(response, list):
                # If it's a list of lists (wrapped response), extract the first embedding
                if len(response) > 0 and isinstance(response[0], (list, tuple)):
                    return response[0]
                # If it's a simple list, return as-is
                return response
            
            raise ValueError(f"Unexpected embedding response format: {type(response)}")
            
        except Exception as e:
            raise RuntimeError(f"Error generating embedding: {str(e)}")
