from huggingface_hub import InferenceClient
from app.core.config import settings


class LLMService:

    client = InferenceClient(
        provider="hf-inference",
        api_key=settings.HF_API_KEY,
    )

    model_name = "mistralai/Mistral-7B-Instruct-v0.2"

    @staticmethod
    def generate(prompt: str) -> str:
        response = LLMService.client.text_generation(
            prompt,
            model=LLMService.model_name,
            max_new_tokens=300,
            temperature=0.3,
            return_full_text=False,
        )

        return response.strip()
