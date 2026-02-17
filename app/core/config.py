import os

class Settings:
    USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

settings = Settings()

