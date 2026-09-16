# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
<<<<<<< HEAD
    PROJECT_NAME: str = "VitalGate AI API"
=======
    PROJECT_NAME: str = "CareTaker AI API"
>>>>>>> team/main
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Supabase Settings
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # LLM Settings
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
