"""
Configuration management for the application
"""
import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip
    pass


class Config:
    """Application configuration"""
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def is_openai_enabled(cls) -> bool:
        """Check if OpenAI is configured and available"""
        return cls.OPENAI_API_KEY is not None and cls.OPENAI_API_KEY != ""
    
    @classmethod
    def validate_config(cls) -> dict:
        """Validate configuration and return status"""
        return {
            "openai_configured": cls.is_openai_enabled(),
            "openai_model": cls.OPENAI_MODEL if cls.is_openai_enabled() else "Not configured",
            "debug_mode": cls.DEBUG,
            "log_level": cls.LOG_LEVEL
        }


# Global config instance
config = Config()
