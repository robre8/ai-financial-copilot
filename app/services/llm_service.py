from huggingface_hub import InferenceClient
import requests
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# Direct API endpoint for Huggingface Inference API
HF_API_BASE = "https://router.huggingface.co/models"
HF_MODEL = "distilgpt2"
HF_HEADERS = {
    "Authorization": f"Bearer {settings.HF_API_KEY}"
}


class LLMService:

    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

    model_name = "distilgpt2"

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text from prompt using EleutherAI/gpt-neo-125M."""
        try:
            logger.info("=== LLM Generation Start ===")
            logger.info("Calling HF API with %s", HF_MODEL)
            logger.info("Prompt preview: %s...", prompt[:100])
            
            url = f"{HF_API_BASE}/{HF_MODEL}"
            payload = {"inputs": prompt}
            logger.info("URL: %s", url)
            logger.info("Auth header present: %s", "YES" if HF_HEADERS.get("Authorization") else "NO")
            
            response = requests.post(
                url,
                headers=HF_HEADERS,
                json=payload,
                timeout=60
            )
            
            logger.info("HF API response status: %d", response.status_code)
            
            if response.status_code != 200:
                logger.error("HF API returned %d: %s", response.status_code, response.text[:200])
                raise RuntimeError(f"HF API error: {response.status_code}")
            
            data = response.json()
            logger.info("LLM response type: %s", type(data))
            
            # Parse response from HF API
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                if isinstance(result, dict) and "generated_text" in result:
                    return result["generated_text"].strip()
                return str(result).strip()
            
            if isinstance(data, dict):
                if "generated_text" in data:
                    return data["generated_text"].strip()
                return str(data).strip()
            
            return str(data).strip()

        except Exception as e:
            tb = traceback.format_exc()
            logger.error("LLM generation failed: %s\nTraceback:\n%s", repr(e), tb)
            raise RuntimeError(f"Error generating text: {repr(e)}")



