from huggingface_hub import InferenceClient
from app.core.config import settings


class LLMService:

    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

    # Use a model that's available in free tier
    model_name = "google/flan-t5-large"
            temperature=0.3,
            return_full_text=False,
        )

        return response.strip()
