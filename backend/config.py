"""
Configuration module for loading and validating environment variables.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    pinecone_api_key: str
    pinecone_index_name: str
    edenai_api_key: str
    chat_groq_api_key: str
    
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/rag_news_tool"
    mongodb_db_name: str = "rag_news_tool"
    
    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Optional settings
    environment: str = "development"
    debug: bool = True
    
    # CORS settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    settings_instance = Settings()
    
    # Add SSL/TLS parameters to MongoDB URI for Python 3.13 compatibility
    if "mongodb+srv://" in settings_instance.mongodb_uri:
        # Parse and add necessary SSL parameters
        if "?" in settings_instance.mongodb_uri:
            settings_instance.mongodb_uri += "&tlsAllowInvalidCertificates=true&tls=true"
        else:
            settings_instance.mongodb_uri += "?tlsAllowInvalidCertificates=true&tls=true"
    
    return settings_instance


# Global settings instance
settings = get_settings()
