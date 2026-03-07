"""Application configuration using pydantic-settings."""

import os
from functools import lru_cache
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="腐蚀与应力在线监测平台 V2.0", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/soundsofts",
        alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/soundsofts",
        alias="DATABASE_URL_SYNC",
    )

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    jwt_secret: str = Field(
        default="change-me-in-production-use-long-random-string",
        alias="JWT_SECRET",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=120, alias="JWT_EXPIRE_MINUTES")

    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    onnx_model_path: str = Field(default="./model-serving/onnx_models", alias="ONNX_MODEL_PATH")
    torchserve_url: str = Field(default="http://localhost:8080", alias="TORCHSERVE_URL")
    mlflow_tracking_uri: str = Field(default="http://localhost:5000", alias="MLFLOW_TRACKING_URI")

    upload_dir: str = Field(default="/tmp/uploads" if os.environ.get("VERCEL") else "./uploads", alias="UPLOAD_DIR")
    report_output_dir: str = Field(default="/tmp/reports" if os.environ.get("VERCEL") else "./reports", alias="REPORT_OUTPUT_DIR")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
