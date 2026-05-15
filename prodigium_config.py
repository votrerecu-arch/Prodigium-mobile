from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    AI_NAME: str = "KmerSource AI"
    AI_VERSION: str = "1.0.0"
    DEPLOY_MODE: str = "console"  # console, hybrid, api
    CORTEX_MODE: str = "standard"
    LIBERTAS_DEFAULT_LEVEL: str = "PUBLIC"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
