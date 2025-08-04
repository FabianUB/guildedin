import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "GuildedIn"
    debug: bool = True
    
    # Database - SQLite for development, PostgreSQL for production
    database_url: str = "sqlite:///./guildedin.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use PostgreSQL in production
        if os.getenv("ENVIRONMENT") == "production":
            self.database_url = os.getenv("DATABASE_URL", "postgresql://guildedin:guildedin@localhost/guildedin_db")

settings = Settings()