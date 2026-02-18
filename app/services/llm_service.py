from huggingface_hub import InferenceClient
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# 🔹 Model configuration
HF_MODEL = "distilgpt2"


class LLMService:

    # 🔹 Use official InferenceClient for text generation
    client = InferenceClient(
        api_key=settings.HF_TOKEN,
    )

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text using distilgpt2 model via InferenceClient."""
        try:
            logger.info("=== LLM Generation Start ===")
            logger.info("Calling HF API with %s via InferenceClient", HF_MODEL)
            logger.info("Prompt preview: %s...", prompt[:100])
            
            # Use InferenceClient.text_generation() - more reliable than direct HTTP
            response = LLMService.client.text_generation(
                prompt=prompt,
                model=HF_MODEL,
                max_new_tokens=300,
                temperature=0.3,
            )
            
            logger.info("LLM response type: %s", type(response))
            logger.info("Generated text length: %d chars", len(str(response)))
            
            # Handle response - InferenceClient returns string directly
            if isinstance(response, str):
                return response.strip()
            
            # Fallback if response is dict
            if isinstance(response, dict) and "generated_text" in response:
                return response["generated_text"].strip()
            
            return str(response).strip()

        except Exception as e:
            tb = traceback.format_exc()
            logger.error("LLM generation failed: %s\nTraceback:\n%s", repr(e), tb)
            raise RuntimeError(f"Error generating text: {repr(e)}")



