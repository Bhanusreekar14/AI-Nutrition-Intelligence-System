from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Nutrition Intelligence System"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "your-supabase-anon-key")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_SECRET_KEY", "your-service-role-key"))
    SUPABASE_SECRET_KEY: str = os.getenv("SUPABASE_SECRET_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-service-role-key"))
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "your-jwt-secret")
    
    # Food APIs
    USDA_API_KEY: str = os.getenv("USDA_API_KEY", "DEMO_KEY")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
