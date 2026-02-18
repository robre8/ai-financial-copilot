import requests
import gc
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# 🔹 Huggingface API configuration
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_HEADERS = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
HF_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.1",
    "google/flan-t5-large",
    "EleutherAI/gpt-neo-125m",
]


class LLMService:

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text using Huggingface Inference API"""
        try:
            for model in HF_MODELS:
                try:
                    url = f"{HF_API_BASE}/{model}"
                    
                    payload = {"inputs": prompt}
                    response = requests.post(
                        url,
                        headers=HF_HEADERS,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # 🔹 Memory cleanup
                        del response
                        gc.collect()
                        
                        if isinstance(result, list) and len(result) > 0:
                            if isinstance(result[0], dict) and 'generated_text' in result[0]:
                                return result[0]['generated_text'].strip()
                        return str(result)
                    else:
                        continue
                        
                except Exception as model_err:
                    logger.warning(f"Model {model} failed: {repr(model_err)}")
                    continue
            
            raise RuntimeError("All models exhausted without success")

        except Exception as e:
            logger.error("LLM generation failed: %s", repr(e))
            raise RuntimeError(f"Error generating text: {repr(e)}")



