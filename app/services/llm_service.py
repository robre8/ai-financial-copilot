from huggingface_hub import InferenceClient
from app.core.config import settings


class LLMService:

    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

    # Use a model that's available in free tier
    model_name = "google/flan-t5-large"

    @staticmethod
    def generate(prompt: str) -> str:
        try:
            response = LLMService.client.text_generation(
                prompt,
                model=LLMService.model_name,
                max_new_tokens=300,
                temperature=0.3,
                return_full_text=False,
            )

            # Normalize possible response formats
            if isinstance(response, list):
                first = response[0]
                if isinstance(first, dict) and "generated_text" in first:
                    return first["generated_text"].strip()
                return str(first).strip()

            if isinstance(response, dict):
                return response.get("generated_text", str(response)).strip()

            return str(response).strip()

        except Exception as e:
            raise RuntimeError(f"Error generating text: {e}")
