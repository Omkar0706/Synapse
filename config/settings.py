# config/settings.py - Alternative: Define all expected fields
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    # Your existing fields
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    LM_STUDIO_BASE_URL: str = "http://localhost:1234/v1"
    LM_STUDIO_API_KEY: str = "lm-studio"
    USE_LM_STUDIO: bool = True
    REDIS_URL: str = "redis://localhost:6379"
    MAX_ITERATIONS: int = 10
    CONFIDENCE_THRESHOLD: float = 0.8
    HUMAN_ESCALATION_THRESHOLD: float = 0.6
    
    # Add the missing fields that were causing errors
    default_model: str = "gpt-4"
    environment: str = "development"
    log_level: str = "INFO"
    redis_host: str = "localhost"
    redis_port: str = "6379"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

config = Config()
