import requests
from app.core.config import settings


HF_EMBED_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

headers = {
    "Authorization": f"Bearer {settings.HF_API_KEY}"
}


class EmbeddingService:

    # 🔹 Dimensión del modelo
    dimension = 384

    @staticmethod
    def embed_text(text: str):
        payload = {"inputs": text}

        response = requests.post(
            HF_EMBED_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        # 🔹 HF devuelve lista directamente
        if isinstance(data, list):
            if isinstance(data[0], list):
                return data[0]
            return data

        raise ValueError("Unexpected embedding response format")
