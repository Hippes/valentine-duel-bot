"""
Configuration module for Valentine Duel Bot
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Bot
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Admin
    ADMIN_USERNAME: str = Field("admin", env="ADMIN_USERNAME")
    ADMIN_PASSWORD: str = Field(..., env="ADMIN_PASSWORD")
    ADMIN_SECRET_KEY: str = Field(..., env="ADMIN_SECRET_KEY")
    
    # Rewards
    PROMO_CODE: str = Field("SALE20%", env="PROMO_CODE")
    STICKER_PACK_URL: str = Field(..., env="STICKER_PACK_URL")
    
    # Redis (Optional)
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    
    # Bot Settings
    REMINDER_TIMEOUT: int = Field(180, env="REMINDER_TIMEOUT")  # 3 minutes
    MAX_CONCURRENT_DUELS: int = Field(100, env="MAX_CONCURRENT_DUELS")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Initialize settings
settings = Settings()
