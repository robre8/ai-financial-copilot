import gc
import time
from huggingface_hub import InferenceClient
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# 🔹 Huggingface API configuration
HF_API_KEY = settings.HF_TOKEN
HF_MODELS = [
    "google/flan-t5-small",
    "gpt2",
    "facebook/opt-350m",
    "distilgpt2",
]


class LLMService:

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text using Huggingface Inference API via InferenceClient"""
        try:
            client = InferenceClient(token=HF_API_KEY)
            
            for model_name in HF_MODELS:
                try:
                    logger.info(f"Trying model: {model_name}")
                    
                    # 🔹 Use text_generation for GPT models
                    if "gpt" in model_name.lower() or "opt" in model_name.lower():
                        result = client.text_generation(
                            prompt=prompt,
                            model=model_name,
                            max_new_tokens=200,
                            temperature=0.7
                        )
                        logger.info(f"✅ Success with model: {model_name}")
                        # 🔹 Memory cleanup
                        gc.collect()
                        return result.strip()
                    
                    # 🔹 Use text2text_generation for T5 models
                    else:
                        result = client.text2text_generation(
                            text=prompt,
                            model=model_name,
                            max_length=200
                        )
                        logger.info(f"✅ Success with model: {model_name}")
                        # 🔹 Memory cleanup
                        gc.collect()
                        return result.strip()
                    
                except Exception as model_err:
                    logger.warning(f"Model {model_name} failed: {repr(model_err)}")
                    continue
            
            raise RuntimeError("All models exhausted without success")

        except Exception as e:
            logger.error("LLM generation failed: %s", repr(e))
            raise RuntimeError(f"Error generating text: {repr(e)}")



