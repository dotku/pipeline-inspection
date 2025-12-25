"""
Configuration management for Pipeline Inspection System
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Camera
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480
    CAMERA_FPS: int = 30

    # Model
    MODEL_PATH: str = "../models/yolov8n.pt"
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45

    # Detection Classes
    DEFECT_CLASSES: str = "foreign_object,crack,rust,corrosion,sediment,leak"

    @property
    def defect_classes_list(self) -> List[str]:
        return [cls.strip() for cls in self.DEFECT_CLASSES.split(",")]

    # Reports
    REPORTS_DIR: str = "../reports"
    ENABLE_PDF_REPORT: bool = True
    ENABLE_JSON_REPORT: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure reports directory exists
Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
