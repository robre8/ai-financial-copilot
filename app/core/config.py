from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 🔹 Huggingface Inference API token
    HF_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        # Support both HF_TOKEN and legacy HF_API_KEY names
        fields = {
            "HF_TOKEN": {"env": ["HF_TOKEN", "HF_API_KEY"]}
        }

    def validate(self):
        """Validate critical configuration"""
        if not self.HF_TOKEN:
            raise ValueError(
                "❌ HF_TOKEN is missing. "
                "Please set it in environment variables or .env file. "
                "Get one from: https://huggingface.co/settings/tokens"
            )
        if not self.HF_TOKEN.startswith("hf_"):
            raise ValueError(
                "❌ HF_TOKEN format is invalid. "
                "It should start with 'hf_'"
            )


settings = Settings()
# Don't validate on import - validate on first use instead
