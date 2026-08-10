"""
Configuration Module
====================
Centralizes all API keys, model settings, and application constants.
Now uses OpenRouter API (FREE models available).
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Central configuration class for the entire application"""

    # ============================================
    # API Configuration - OpenRouter (FREE)
    # ============================================
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"

    # ============================================
    # Model Configuration (FREE models from OpenRouter)
    # ============================================
    # Available FREE models (all end with ':free'):
    # - inclusionai/ling-3.0-tiny:free
    # - meta-llama/llama-3.1-8b-instruct:free
    # - inclusionai/ling-3.0-tiny:free
    # - mistralai/mistral-7b-instruct:free
    # - microsoft/phi-3-mini-128k-instruct:free
    
    DEFAULT_MODEL: str = "inclusionai/ling-3.0-tiny:free"
    FALLBACK_MODEL: str = "inclusionai/ling-3.0-tiny:free"
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    REQUEST_TIMEOUT: int = 30

    # ============================================
    # Agent Configuration
    # ============================================
    AGENT_NAME: str = "MediBot"
    AGENT_DESCRIPTION: str = "AI Agent for Medical Operations Dashboard"
    AGENT_VERSION: str = "1.0.0"

    # ============================================
    # Application Settings
    # ============================================
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    MAX_RETRIES: int = 3
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ============================================
    # Medical Domain Constants (for Team A)
    # ============================================
    SUPPORTED_DEPARTMENTS = [
        "Cardiology",
        "Neurology",
        "Orthopedics",
        "Pediatrics",
        "Emergency",
        "General Medicine"
    ]

    EMERGENCY_KEYWORDS = [
        "emergency", "urgent", "critical", "severe",
        "bleeding", "unconscious", "heart attack", "stroke"
    ]

    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configurations are set."""
        errors = []

        if not cls.OPENROUTER_API_KEY:
            errors.append("❌ OPENROUTER_API_KEY not found in .env file")

        if cls.DEFAULT_TEMPERATURE < 0 or cls.DEFAULT_TEMPERATURE > 1:
            errors.append("❌ Temperature must be between 0 and 1")

        if errors:
            error_msg = "\n".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("✅ Configuration validated successfully")
        return True

    @classmethod
    def display(cls) -> None:
        """Display current configuration."""
        print("\n" + "=" * 60)
        print(f"  {cls.AGENT_NAME} - Configuration")
        print("=" * 60)
        print(f"  📌 Agent Name       : {cls.AGENT_NAME}")
        print(f"  📌 Version          : {cls.AGENT_VERSION}")
        print(f"  📌 Default Model    : {cls.DEFAULT_MODEL}")
        print(f"  📌 Temperature      : {cls.DEFAULT_TEMPERATURE}")
        print(f"  📌 Max Tokens       : {cls.MAX_TOKENS}")
        print(f"  📌 Debug Mode       : {cls.DEBUG_MODE}")
        print(f"  📌 Provider         : OpenRouter (FREE)")

        if cls.OPENROUTER_API_KEY:
            masked_key = cls.OPENROUTER_API_KEY[:12] + "..." + cls.OPENROUTER_API_KEY[-4:]
            print(f"  📌 API Key          : {masked_key}")
        else:
            print(f"  📌 API Key          : ❌ NOT SET")

        print(f"  📌 Departments      : {len(cls.SUPPORTED_DEPARTMENTS)} configured")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        Config.validate()
        Config.display()
        print("✅ All checks passed! Ready to build agents.\n")
    except ValueError as e:
        print(f"\n{e}\n")
        print("💡 Fix: Make sure your .env file has: OPENROUTER_API_KEY=your_key_here\n")
