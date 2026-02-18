import requests
import gc
import time
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# 🔹 Huggingface API configuration
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_HEADERS = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
HF_MODELS = [
    "google/flan-t5-base",  # Faster, more reliable
    "mistralai/Mistral-7B-Instruct-v0.1",
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
                        timeout=45  # Increased timeout for large models
                    )
                    
                    # 🔹 Enhanced logging
                    logger.info(f"Model {model} returned status: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # 🔹 Memory cleanup
                        del response
                        gc.collect()
                        
                        if isinstance(result, list) and len(result) > 0:
                            if isinstance(result[0], dict):
                                # Check for common response keys from different models
                                for key in ['generated_text', 'summary_text', 'translation_text']:
                                    if key in result[0]:
                                        logger.info(f"✅ Success with model: {model}")
                                        return result[0][key].strip()
                        return str(result)
                    
                    elif response.status_code == 503:
                        # Model is loading - wait and retry once
                        error_data = response.json()
                        estimated_time = error_data.get('estimated_time', 20)
                        logger.warning(f"Model {model} loading... waiting {estimated_time}s")
                        
                        if estimated_time < 30:
                            time.sleep(min(estimated_time + 2, 30))
                            # Retry
                            response = requests.post(url, headers=HF_HEADERS, json=payload, timeout=45)
                            if response.status_code == 200:
                                result = response.json()
                                if isinstance(result, list) and len(result) > 0:
                                    if isinstance(result[0], dict):
                                        # Check for common response keys from different models
                                        for key in ['generated_text', 'summary_text', 'translation_text']:
                                            if key in result[0]:
                                                return result[0][key].strip()
                                return str(result)
                        continue
                    
                    else:
                        # Log error details
                        try:
                            error_msg = response.json()
                            logger.warning(f"Model {model} failed: {response.status_code} - {error_msg}")
                        except Exception:
                            logger.warning(f"Model {model} failed: {response.status_code} - {response.text[:200]}")
                        continue
                        
                except Exception as model_err:
                    logger.warning(f"Model {model} exception: {repr(model_err)}")
                    continue
            
            raise RuntimeError("All models exhausted without success")

        except Exception as e:
            logger.error("LLM generation failed: %s", repr(e))
            raise RuntimeError(f"Error generating text: {repr(e)}")



