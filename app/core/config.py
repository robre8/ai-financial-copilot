from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    # 🔹 Huggingface API token for embeddings and LLM
    HF_TOKEN: Optional[str] = None

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

    def __init__(self, **data):
        super().__init__(**data)

    def validate(self):
        """Validate critical configuration"""
        if not self.HF_TOKEN:
            raise ValueError(
                "HF_TOKEN is missing. "
                "Please set it in environment variables or .env file. "
                "Get one from: https://huggingface.co/settings/tokens"
            )


settings = Settings()
# Don't validate on import - validate on first use instead
