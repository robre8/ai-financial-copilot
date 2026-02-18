import gc
from huggingface_hub import InferenceClient
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger()

HF_MODELS = [
    "gpt2",
    "distilgpt2",
    "EleutherAI/gpt-neo-125m",
    "facebook/opt-125m",
]


class LLMService:

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text using Huggingface Inference API via InferenceClient"""
        try:
            client = InferenceClient(token=settings.HF_TOKEN)

            for model in HF_MODELS:
                try:
                    logger.info(f"Trying model: {model}")

                    result = client.text_generation(
                        prompt,
                        model=model,
                        max_new_tokens=256,
                        do_sample=True,
                        temperature=0.7,
                    )

                    if result and result.strip():
                        logger.info(f"✅ Success with model: {model}")
                        del client
                        gc.collect()
                        return result.strip()
                    else:
                        logger.warning(f"Model {model} returned empty result")
                        continue

                except Exception as model_err:
                    logger.warning(f"Model {model} failed: {repr(model_err)}")
                    continue

            raise RuntimeError("All models exhausted without success")

        except Exception as e:
            logger.error("LLM generation failed: %s", repr(e))
            raise RuntimeError(f"Error generating text: {repr(e)}")



