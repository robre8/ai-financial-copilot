from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    # 🔹 Huggingface Inference API token
    HF_TOKEN: Optional[str] = None
    # 🔹 Groq API token for LLM generation
    GROQ_API_KEY: Optional[str] = None

    model_config = ConfigDict(
        env_file=".env",
        # Support both HF_TOKEN and legacy HF_API_KEY names
        extra="ignore"
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Check for legacy HF_API_KEY if HF_TOKEN not set
        if not self.HF_TOKEN:
            import os
            self.HF_TOKEN = os.getenv("HF_API_KEY")

    def validate(self):
        """Validate critical configuration"""
        if not self.GROQ_API_KEY:
            raise ValueError(
                "❌ GROQ_API_KEY is missing. "
                "Please set it in environment variables or .env file. "
                "Get one from: https://console.groq.com"
            )
        if not self.GROQ_API_KEY.startswith("gsk_"):
            raise ValueError(
                "❌ GROQ_API_KEY format is invalid. "
                "It should start with 'gsk_'"
            )


settings = Settings()
# Don't validate on import - validate on first use instead
