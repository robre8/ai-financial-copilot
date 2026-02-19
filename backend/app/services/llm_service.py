import gc
from groq import Groq
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger()

GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
]


class LLMService:

    @staticmethod
    def generate(prompt: str) -> tuple[str, str]:
        """Generate text using Groq API and return (text, model)."""
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)

            for model in GROQ_MODELS:
                try:
                    logger.info(f"Trying Groq model: {model}")

                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a helpful financial analyst assistant. Answer based only on the provided context."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=512,
                        temperature=0.7,
                    )

                    result = response.choices[0].message.content

                    if result and result.strip():
                        logger.info(f"✅ Success with Groq model: {model}")
                        del client
                        gc.collect()
                        return result.strip(), model

                except Exception as model_err:
                    logger.warning(f"Groq model {model} failed: {repr(model_err)}")
                    continue

            raise RuntimeError("All Groq models exhausted without success")

        except Exception as e:
            logger.error("LLM generation failed: %s", repr(e))
            raise RuntimeError(f"Error generating text: {repr(e)}")



