from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    # 🔹 Huggingface API token for embeddings
    HF_TOKEN: Optional[str] = None
    
    # 🔹 Groq API token for LLM
    GROQ_API_KEY: Optional[str] = None

    # 🔹 Frontend origins for CORS (comma-separated)
    FRONTEND_ORIGINS: str = "http://localhost:5173"
    
    # � Database URL for PostgreSQL + pgvector
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_copilot"
    
    # �🔐 API Keys (comma-separated: key:scope:name format)
    # Example: "abc123:admin:DevKey,xyz789:read:DemoKey"
    API_KEYS: str = "demo-key-12345:admin:Demo"
    
    # ⏱️ Timeout settings (seconds)
    LLM_TIMEOUT: int = 30
    EMBEDDING_TIMEOUT: int = 20
    
    # 🔄 Retry settings
    MAX_RETRIES: int = 3
    RETRY_MULTIPLIER: int = 2  # Exponential backoff multiplier

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
    
    def get_api_keys(self) -> dict:
        """
        Parse API_KEYS into a dictionary.
        
        Returns:
            dict: {api_key: {"scope": "read", "name": "KeyName"}}
        """
        keys = {}
        for key_entry in self.API_KEYS.split(","):
            parts = key_entry.strip().split(":")
            if len(parts) >= 2:
                key = parts[0]
                scope = parts[1] if len(parts) > 1 else "read"
                name = parts[2] if len(parts) > 2 else "Unknown"
                keys[key] = {"scope": scope, "name": name}
        return keys


settings = Settings()
# Don't validate on import - validate on first use instead
