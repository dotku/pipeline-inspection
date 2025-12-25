"""
Configuration management for Pipeline Inspection System
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Camera (can be USB index or URL for RTSP/HTTP)
    CAMERA_INDEX: Union[int, str] = "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4"
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480
    CAMERA_FPS: int = 30

    @field_validator('CAMERA_INDEX', mode='before')
    @classmethod
    def parse_camera_index(cls, v):
        """Convert numeric strings to int for USB cameras"""
        if isinstance(v, str):
            # Try to convert to int for USB camera indices
            try:
                return int(v)
            except ValueError:
                # Not a number, return as-is (URL)
                return v
        return v

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
