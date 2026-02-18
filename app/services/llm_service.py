import requests
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# 🔹 Model configuration
# Using gpt2 - public model always available in HF Inference API
HF_MODEL = "gpt2"
HF_API_URL = "https://router.huggingface.co/hf-inference/models"


class LLMService:

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text using distilgpt2 model via Huggingface Inference API."""
        try:
            logger.info("=== LLM Generation Start ===")
            logger.info("Calling HF API with %s", HF_MODEL)
            logger.info("Prompt preview: %s...", prompt[:100])
            
            url = f"{HF_API_URL}/gpt2/pipeline/text-generation"
            headers = {
                "Authorization": f"Bearer {settings.HF_TOKEN}",
            }
            payload = {"inputs": prompt}
            
            logger.info("URL: %s", url)
            logger.info("Auth header present: YES")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            logger.info("HF API response status: %d", response.status_code)
            
            if response.status_code != 200:
                logger.error("HF API returned %d: %s", response.status_code, response.text[:500])
                raise RuntimeError(f"HF API error: {response.status_code}")
            
            data = response.json()
            logger.info("LLM response type: %s", type(data))
            
            # Parse response - HF Inference API returns list of dicts
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                if isinstance(result, dict) and "generated_text" in result:
                    # Return only the generated part, not including the input prompt
                    full_text = result["generated_text"]
                    # Remove the input prompt from the response
                    if full_text.startswith(prompt):
                        generated = full_text[len(prompt):].strip()
                    else:
                        generated = full_text.strip()
                    return generated if generated else full_text
                return str(result).strip()
            
            if isinstance(data, dict):
                if "generated_text" in data:
                    full_text = data["generated_text"]
                    if full_text.startswith(prompt):
                        generated = full_text[len(prompt):].strip()
                    else:
                        generated = full_text.strip()
                    return generated if generated else full_text
                return str(data).strip()
            
            return str(data).strip()

        except Exception as e:
            tb = traceback.format_exc()
            logger.error("LLM generation failed: %s\nTraceback:\n%s", repr(e), tb)
            raise RuntimeError(f"Error generating text: {repr(e)}")



