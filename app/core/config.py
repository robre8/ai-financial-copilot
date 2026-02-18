from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HF_API_KEY: str

    class Config:
        env_file = ".env"

    def validate(self):
        """Validate critical configuration on startup"""
        if not self.HF_API_KEY or not self.HF_API_KEY.startswith("hf_"):
            raise ValueError(
                "❌ HF_API_KEY is missing or invalid. "
                "Please set it in .env file. "
                "Get one from: https://huggingface.co/settings/tokens"
            )


settings = Settings()
# Validate on startup
settings.validate()
