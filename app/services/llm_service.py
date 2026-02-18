import os
from groq import Groq
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger()

# 🔹 Groq configuration - Free tier with high-quality models
GROQ_MODEL = "llama-3.1-8b-instant"


class LLMService:
    # 🔹 Groq client initialized with API key
    @staticmethod
    def _get_client():
        """Initialize Groq client"""
        return Groq(api_key=settings.GROQ_API_KEY)

    @staticmethod
    def generate(prompt: str) -> str:
        """Generate text using Groq's Llama 3.1 model."""
        try:
            logger.info("=== LLM Generation Start ===")
            logger.info("Calling Groq API with %s", GROQ_MODEL)
            logger.info("Prompt preview: %s...", prompt[:100])
            
            client = LLMService._get_client()
            
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.3,
                top_p=0.9,
            )
            
            logger.info("Groq API response status: 200 (success)")
            logger.info("Generated text length: %d chars", len(response.choices[0].message.content))
            
            return response.choices[0].message.content.strip()

        except Exception as e:
            tb = traceback.format_exc()
            logger.error("LLM generation failed: %s\nTraceback:\n%s", repr(e), tb)
            raise RuntimeError(f"Error generating text: {repr(e)}")



