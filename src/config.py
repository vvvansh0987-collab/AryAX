"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    app_name: str = "AryaX Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str = "postgresql+asyncpg://aryax:aryax_password@localhost:5432/aryax_db"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 300  # 5 minutes
    redis_session_ttl: int = 86400  # 24 hours
    
    # Elasticsearch
    elasticsearch_hosts: list = ["http://localhost:9200"]
    elasticsearch_index_prefix: str = "aryax"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 1
    jwt_refresh_expiration_days: int = 7
    
    # API Keys
    api_key_prefix: str = "sk_live"
    
    # Stripe
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # External APIs
    gemini_api_keys: list = []
    openai_api_key: Optional[str] = None
    
    # Security
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    allowed_hosts: list = ["localhost", "127.0.0.1"]
    
    # Encryption
    encryption_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
