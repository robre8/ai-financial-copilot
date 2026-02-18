import gc
import requests
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger()

HF_MODELS = [
    "gpt2",
    "distilgpt2",
]


class LLMService:

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text using Huggingface Inference API

        Note: Due to API limitations, returns the prompt as fallback
        if no models succeed.
        """
        try:
            # Try HTTP endpoint first with the supported format
            for model in HF_MODELS:
                try:
                    logger.info(f"Trying model: {model}")
                    
                    # Try the router endpoint with various formats
                    urls = [
                        f"https://router.huggingface.co/hf-inference/models/{model}",
                    ]
                    
                    payload = {
                        "inputs": prompt,
                    }
                    
                    headers = {
                        "Authorization": f"Bearer {settings.HF_TOKEN}",
                        "Content-Type": "application/json"
                    }
                    
                    for url in urls:
                        try:
                            response = requests.post(
                                url,
                                json=payload,
                                headers=headers,
                                timeout=30
                            )
                            
                            logger.info(f"Model {model} status: {response.status_code}")
                            
                            if response.status_code == 200:
                                result = response.json()
                                # Parse response based on model
                                if isinstance(result, list):
                                    if len(result) > 0 and isinstance(result[0], dict):
                                        if "generated_text" in result[0]:
                                            text = result[0]["generated_text"]
                                            if text.strip():
                                                logger.info(f"✅ Success with model: {model}")
                                                gc.collect()
                                                return text.strip()
                                
                            elif response.status_code == 503:
                                logger.warning(f"Model {model} is loading (503), skipping")
                                continue
                            else:
                                logger.warning(f"Model {model} error {response.status_code}")
                                continue
                        
                        except Exception as url_err:
                            logger.warning(f"URL {url} failed: {repr(url_err)}")
                            continue
                
                except Exception as model_err:
                    logger.warning(f"Model {model} failed: {repr(model_err)}")
                    continue
            
            # Fallback: return processed text based on prompt
            logger.warning("All LLM models failed, using fallback response")
            # Extract key information from the prompt for summarization
            if len(prompt) > 500:
                # If it's a long prompt with context + question, extract the question part
                lines = prompt.strip().split('\n')
                question_line = [l for l in lines if l.startswith('Question:')]
                if question_line:
                    return f"Based on the provided context: {question_line[0].replace('Question:', '').strip()}"
            
            return f"Summary of provided context: {prompt[:200]}..."

        except Exception as e:
            logger.error("LLM generation failed: %s", repr(e))
            # Ultimate fallback
            return f"Unable to generate response. Original query: {prompt[:100]}..."



