from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Invoice Generator API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database settings
    DATABASE_URL: Optional[str] = "sqlite:///./invoice_generator.db"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()