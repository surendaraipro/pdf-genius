"""
Configuration settings for PDF Genius
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "PDF Genius"
    app_version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/pdf_genius"
    )
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Storage
    storage_type: str = os.getenv("STORAGE_TYPE", "local")  # local, s3, backblaze
    s3_bucket: Optional[str] = os.getenv("S3_BUCKET")
    s3_access_key: Optional[str] = os.getenv("S3_ACCESS_KEY")
    s3_secret_key: Optional[str] = os.getenv("S3_SECRET_KEY")
    s3_endpoint: Optional[str] = os.getenv("S3_ENDPOINT")
    
    # AI Services
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    use_local_llm: bool = os.getenv("USE_LOCAL_LLM", "True").lower() == "true"
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Stripe
    stripe_secret_key: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # File upload limits
    max_upload_size_mb: int = 100  # 100MB max file size
    allowed_file_types: list = [".pdf"]
    
    # Temporary storage
    temp_dir: str = "/tmp/pdf_genius"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Create temp directory if it doesn't exist
os.makedirs(settings.temp_dir, exist_ok=True)