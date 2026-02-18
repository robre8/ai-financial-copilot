from huggingface_hub import InferenceClient
import requests
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# Direct API endpoint for Huggingface Inference API - try multiple models
HF_MODELS = [
    "gpt2",
    "distilgpt2",
]

# Primary: try requests to a working model
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_HEADERS = {
    "Authorization": f"Bearer {settings.HF_API_KEY}"
}


class LLMService:

    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

    model_name = "gpt2"

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text from prompt. Fallback to simple processing if API fails."""
        try:
            # Try to call HF API
            logger.info("Attempting LLM generation")
            
            for model in HF_MODELS:
                url = f"{HF_API_BASE}/{model}"
                try:
                    payload = {"inputs": prompt}
                    response = requests.post(
                        url,
                        headers=HF_HEADERS,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info("LLM success with model %s", model)
                        
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
                    else:
                        logger.warning("Model %s returned status %d, trying next", model, response.status_code)
                        
                except Exception as model_err:
                    logger.warning("Model %s failed: %s, trying next", model, repr(model_err))
                    continue
            
            # If all models fail, return a helpful fallback
            logger.error("All LLM models exhausted, using fallback response")
            raise RuntimeError("All LLM models unavailable")

        except Exception as e:
            logger.error("LLM generation failed: %s", repr(e))
            # Return a safe fallback response
            return "I was unable to generate a response at this time, but the relevant context from your documents has been retrieved. Please contact support if the issue persists."


