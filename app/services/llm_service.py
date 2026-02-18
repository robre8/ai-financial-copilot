from huggingface_hub import InferenceClient
import requests
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# Direct API endpoint for Huggingface Inference API
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"
HF_HEADERS = {
    "Authorization": f"Bearer {settings.HF_API_KEY}"
}


class LLMService:

    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

    # Use a model that's available in free tier
    model_name = "gpt2"

    @staticmethod
    def generate(prompt: str) -> str:
        try:
            # Use direct HTTP API instead of client object
            logger.info("Calling HF API directly for text_generation")
            
            payload = {"inputs": prompt}
            response = requests.post(
                HF_API_URL,
                headers=HF_HEADERS,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info("Raw HF response type: %s", type(data))
            
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
            logger.error("LLM generation failed: %s", tb)
            raise RuntimeError(f"Error generating text: {repr(e)}")

