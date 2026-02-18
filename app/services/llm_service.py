from huggingface_hub import InferenceClient
from app.core.config import settings
from app.core.logger import setup_logger
import traceback


class LLMService:

    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

logger = setup_logger()

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

            # Log raw response for debugging
            try:
                logger.info("LLM raw response type=%s", type(response))
                logger.debug("LLM raw response repr: %s", repr(response))
            except Exception:
                logger.debug("Failed to log raw response")

            # Normalize possible response formats
            if isinstance(response, list):
                first = response[0]
                if isinstance(first, dict) and "generated_text" in first:
                    return first["generated_text"].strip()
                # if it's a list of strings or primitives
                return str(first).strip()

            if isinstance(response, dict):
                # Many HF clients return {'generated_text': '...'} or similar
                if "generated_text" in response:
                    return response["generated_text"].strip()
                # fallback to any top-level text-like keys
                for k in ("generated_text", "text", "content"):
                    if k in response:
                        return str(response[k]).strip()
                return str(response).strip()

            return str(response).strip()

        except Exception as e:
            # Log full traceback for debugging on server
            tb = traceback.format_exc()
            logger.error("LLM generation failed: %s", tb)
            # Re-raise with a repr message so it's not empty
            raise RuntimeError(f"Error generating text: {repr(e)}")
