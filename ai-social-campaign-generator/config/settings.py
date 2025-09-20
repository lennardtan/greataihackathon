from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"

class Settings(BaseSettings):
    # LLM Settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    llm_provider: LLMProvider = LLMProvider.GEMINI
    llm_model: str = "gemini-2.5-flash"
    
    # Image API Settings
    image_api_url: Optional[str] = None
    image_api_key: Optional[str] = None
    
    # Application Settings
    max_retries: int = 3
    timeout: int = 30
    debug: bool = False
    
    # Conversation Settings
    max_conversation_turns: int = 20
    memory_window_size: int = 10
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()