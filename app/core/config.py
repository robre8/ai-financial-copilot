from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    HF_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

    def validate(self):
        """Validate critical configuration"""
        if not self.HF_API_KEY:
            raise ValueError(
                "❌ HF_API_KEY is missing. "
                "Please set it in environment variables or .env file. "
                "Get one from: https://huggingface.co/settings/tokens"
            )
        if not self.HF_API_KEY.startswith("hf_"):
            raise ValueError(
                "❌ HF_API_KEY format is invalid. "
                "It should start with 'hf_'"
            )


settings = Settings()
# Don't validate on import - validate on first use instead
