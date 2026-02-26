import gc
from groq import Groq
from app.core.config import settings
from app.core.logger import setup_logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import httpx

logger = setup_logger()

GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
]


class LLMService:

    @staticmethod
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=settings.RETRY_MULTIPLIER, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectTimeout, ConnectionError)),
        before_sleep=before_sleep_log(logger, logger.level)
    )
    def _call_model_with_retry(client: Groq, model: str, prompt: str) -> tuple[str, str]:
        """
        Call Groq API with retry logic and timeout.
        
        Retries on timeout/connection errors with exponential backoff.
        """
        logger.info(f"Trying Groq model: {model}")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful financial analyst assistant. Answer based only on the provided context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7,
            timeout=settings.LLM_TIMEOUT,  # Configurable timeout
        )

        result = response.choices[0].message.content

        if result and result.strip():
            logger.info(f"✅ Success with Groq model: {model}")
            return result.strip(), model
        
        raise ValueError(f"Empty response from model {model}")

    @staticmethod
    def generate(prompt: str) -> tuple[str, str]:
        """Generate text using Groq API and return (text, model)."""
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)

            for model in GROQ_MODELS:
                try:
                    result, used_model = LLMService._call_model_with_retry(client, model, prompt)
                    del client
                    gc.collect()
                    return result, used_model

                except Exception as model_err:
                    logger.warning(f"Groq model {model} failed after retries: {repr(model_err)}")
                    continue

            raise RuntimeError("All Groq models exhausted without success")

        except Exception as e:
            logger.error("LLM generation failed: %s", repr(e))
            raise RuntimeError(f"Error generating text: {repr(e)}")



