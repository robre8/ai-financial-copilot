from huggingface_hub import InferenceClient
import requests
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# Direct API endpoint for Huggingface Inference API
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_MODEL = "EleutherAI/gpt-neo-125M"
HF_HEADERS = {
    "Authorization": f"Bearer {settings.HF_API_KEY}"
}


class LLMService:

    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

    model_name = "EleutherAI/gpt-neo-125M"

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text from prompt using EleutherAI/gpt-neo-125M."""
        try:
            logger.info("Calling HF API with %s", HF_MODEL)
            
            url = f"{HF_API_BASE}/{HF_MODEL}"
            payload = {"inputs": prompt}
            
            response = requests.post(
                url,
                headers=HF_HEADERS,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error("HF API returned %d: %s", response.status_code, response.text)
                raise RuntimeError(f"HF API error: {response.status_code}")
            
            data = response.json()
            logger.info("LLM success, response type: %s", type(data))
            
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
            logger.error("LLM generation failed: %s", repr(e))
            raise RuntimeError(f"Error generating text: {repr(e)}")



