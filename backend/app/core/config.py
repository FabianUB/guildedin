from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "GuildedIn"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://guildedin:guildedin@localhost/guildedin_db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"

settings = Settings()