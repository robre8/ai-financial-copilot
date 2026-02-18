from huggingface_hub import InferenceClient
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()


class LLMService:

    client = InferenceClient(
        api_key=settings.HF_API_KEY,
    )

    # Use a model that's available in free tier
    model_name = "gpt2"

    @staticmethod
    def generate(prompt: str) -> str:
        try:
            response = LLMService.client.text_generation(
                prompt,
                model=LLMService.model_name,
                max_new_tokens=300,
                temperature=0.3,
                return_full_text=False,
            )

            # If the HF client returns a generator/iterator, materialize it safely
            try:
                if hasattr(response, "__iter__") and not isinstance(response, (str, list, dict)):
                    try:
                        materialized = list(response)
                    except Exception as mat_exc:
                        logger.error("Failed to materialize iterator response: %s", repr(mat_exc))
                        raise RuntimeError("Failed to materialize iterator response")

                    if not materialized:
                        logger.error("LLM client returned no items when materializing iterator")
                        raise RuntimeError("LLM client returned no data")

                    response = materialized[0] if len(materialized) == 1 else materialized
            except RuntimeError:
                # Re-raise runtime errors with clearer message
                raise
            except Exception as mat_outer_exc:
                logger.warning("Non-fatal error while handling iterator: %s", repr(mat_outer_exc))
                # Fall through and try to handle the raw response
                pass

            # Log raw response for debugging
            try:
                logger.info("LLM raw response type=%s", type(response))
                logger.debug("LLM raw response repr: %s", repr(response))
            except Exception:
                logger.debug("Failed to log raw response")

            # Normalize possible response formats
            if isinstance(response, list):
                first = response[0]
                if isinstance(first, dict) and "generated_text" in first:
                    return first["generated_text"].strip()
                # if it's a list of strings or primitives
                return str(first).strip()

            if isinstance(response, dict):
                # Many HF clients return {'generated_text': '...'} or similar
                if "generated_text" in response:
                    return response["generated_text"].strip()
                # fallback to any top-level text-like keys
                for k in ("generated_text", "text", "content"):
                    if k in response:
                        return str(response[k]).strip()
                return str(response).strip()

            return str(response).strip()

        except Exception as e:
            # Log full traceback for debugging on server
            tb = traceback.format_exc()
            logger.error("LLM generation failed: %s", tb)
            # Re-raise with a repr message so it's not empty
            raise RuntimeError(f"Error generating text: {repr(e)}")
