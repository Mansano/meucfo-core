# app/config.py

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "MeuCFO.ai"
    APP_ENV: str = "dev"
    APP_PORT: int = 8000
    APP_HOST: str = "http://localhost:8000"
    APP_SECRET_KEY: str = "your-secret-key-change-in-production"
    APP_ADMIN_MAIL: str = "admin@meucfo.ai"
    APP_ADMIN_PASS: str = "admin123"
    
    # Cloudflare D1
    # Cloudflare D1
    CLOUDFLARE_ACCOUNT_ID: str = ""
    CLOUDFLARE_DATABASE_ID: str = ""
    CLOUDFLARE_API_TOKEN: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_USERNAME: Optional[str] = None
    

    
    # Webhook URLs
    N8N_WEBHOOK_URL: str = "https://your-n8n-instance.com/webhook"
    LLM_WEBHOOK_URL: str = "https://your-llm-service.com/analyze"
    
    # Rate Limiting
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW: int = 900  # 15 minutos em segundos
    RATE_LIMIT_API_CALLS: int = 100
    RATE_LIMIT_API_WINDOW: int = 3600  # 1 hora
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
