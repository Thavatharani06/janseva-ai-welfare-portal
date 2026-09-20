import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JanSeva AI - Multilingual Legal Welfare Assistant"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "janseva-super-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./legal_welfare.db")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # Feature Flags & Integration Settings
    DIGILOCKER_ENABLED: bool = os.getenv("DIGILOCKER_ENABLED", "false").lower() in ("true", "1", "t")
    DIGILOCKER_CLIENT_ID: str = os.getenv("DIGILOCKER_CLIENT_ID", "")
    DIGILOCKER_CLIENT_SECRET: str = os.getenv("DIGILOCKER_CLIENT_SECRET", "")
    DIGILOCKER_REDIRECT_URI: str = os.getenv("DIGILOCKER_REDIRECT_URI", "http://localhost:8501/digilocker/callback")
    DIGILOCKER_AUTH_URL: str = os.getenv("DIGILOCKER_AUTH_URL", "https://api.apisetu.gov.in/digilocker/v1/oauth2/authorize")
    DIGILOCKER_TOKEN_URL: str = os.getenv("DIGILOCKER_TOKEN_URL", "https://api.apisetu.gov.in/digilocker/v1/oauth2/token")
    DIGILOCKER_ISSUED_DOCS_URL: str = os.getenv("DIGILOCKER_ISSUED_DOCS_URL", "https://api.apisetu.gov.in/digilocker/v1/oauth2/file/issued")

    LPG_ENABLED: bool = os.getenv("LPG_ENABLED", "false").lower() in ("true", "1", "t")
    LPG_API_URL: str = os.getenv("LPG_API_URL", "")
    LPG_API_KEY: str = os.getenv("LPG_API_KEY", "")

    class Config:
        case_sensitive = True

settings = Settings()

