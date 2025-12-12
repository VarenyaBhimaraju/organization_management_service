from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    mongodb_url: str
    database_name: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    app_name: str = "Organization Management Service"
    app_version: str = "1.0.0"
    debug: bool = False
    port: int = int(os.getenv("PORT", 8000))
    
    class Config:
        env_file = ".env"  # Ensure this is correctly set to load the .env file
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
