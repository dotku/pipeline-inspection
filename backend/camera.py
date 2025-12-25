"""
Camera interface for pipeline inspection
Handles video capture from USB cameras, RTSP streams, and HTTP video URLs
"""
import cv2
import numpy as np
from typing import Optional, Tuple, Union
import logging
from config import settings

logger = logging.getLogger(__name__)


class Camera:
    """Camera capture and management (USB, RTSP, and HTTP)"""

    def __init__(
        self,
        camera_source: Union[int, str] = None,
        width: int = None,
        height: int = None,
        fps: int = None
    ):
        """
        Initialize camera (USB, RTSP, or HTTP)

        Args:
            camera_source: Camera device index (int), RTSP URL (str), or HTTP video URL (str)
                          Examples:
                          - USB: 0, 1, 2
                          - RTSP: "rtsp://..."
                          - HTTP: "http://..." or "https://..."
            width: Frame width (default from settings)
            height: Frame height (default from settings)
            fps: Target FPS (default from settings)
        """
        self.camera_source = camera_source if camera_source is not None else settings.CAMERA_INDEX
        self.width = width or settings.CAMERA_WIDTH
        self.height = height or settings.CAMERA_HEIGHT
        self.fps = fps or settings.CAMERA_FPS

        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False

        # Detect source type
        if isinstance(self.camera_source, str):
            if self.camera_source.startswith('rtsp://') or self.camera_source.startswith('rtsps://'):
                self.source_type = 'RTSP'
            elif self.camera_source.startswith('http://') or self.camera_source.startswith('https://'):
                self.source_type = 'HTTP'
            else:
                self.source_type = 'RTSP'  # Default for other string formats
        else:
            self.source_type = 'USB'

        # Legacy compatibility
        self.is_rtsp = self.source_type in ['RTSP', 'HTTP']

    def open(self) -> bool:
        """
        Open camera connection (USB, RTSP, or HTTP)

        Returns:
            bool: True if camera opened successfully
        """
        try:
            # Open camera (works for USB, RTSP, and HTTP URLs)
            self.cap = cv2.VideoCapture(self.camera_source)

            if not self.cap.isOpened():
                logger.error(f"Failed to open {self.source_type} source: {self.camera_source}")
                return False

            # Set camera properties (only works for USB cameras)
            if self.source_type == 'USB':
                # USB cameras support setting these properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            else:
                # RTSP/HTTP streams use native resolution/fps
                logger.info(f"{self.source_type} stream opened - using native resolution/fps")

            # Verify settings
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))

            # Format source info
            if self.source_type == 'USB':
                source_info = f"USB Camera {self.camera_source}"
            else:
                # Truncate long URLs for logging
                url_display = str(self.camera_source)[:60] + "..." if len(str(self.camera_source)) > 60 else str(self.camera_source)
                source_info = f"{self.source_type}: {url_display}"

            logger.info(
                f"{source_info} opened: {actual_width}x{actual_height} @ {actual_fps}fps"
            )

            self.is_opened = True
            return True

        except Exception as e:
            logger.error(f"Error opening camera: {e}")
            return False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a single frame from camera

        Returns:
            Tuple of (success: bool, frame: np.ndarray or None)
        """
        if not self.is_opened or self.cap is None:
            logger.warning("Camera not opened")
            return False, None

        ret, frame = self.cap.read()

        if not ret:
            # For video files (not USB cameras), loop back to the beginning
            if self.source_type in ['RTSP', 'HTTP'] and isinstance(self.camera_source, str):
                logger.info("Video ended, looping back to start")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()

                if not ret:
                    logger.warning("Failed to read frame from camera")
                    return False, None
            else:
                logger.warning("Failed to read frame from camera")
                return False, None

        return True, frame

    def read_frame_encoded(self, format: str = ".jpg") -> Tuple[bool, Optional[bytes]]:
        """
        Read frame and encode to JPEG/PNG for web streaming

        Args:
            format: Image format (.jpg or .png)

        Returns:
            Tuple of (success: bool, encoded_image: bytes or None)
        """
        ret, frame = self.read_frame()

        if not ret or frame is None:
            return False, None

        # Encode frame
        ret, buffer = cv2.imencode(format, frame)

        if not ret:
            logger.warning("Failed to encode frame")
            return False, None

        return True, buffer.tobytes()

    def close(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            logger.info("Camera closed")

    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    @staticmethod
    def list_available_cameras(max_index: int = 5) -> list:
        """
        List available USB camera indices

        Args:
            max_index: Maximum camera index to check

        Returns:
            List of available camera indices
        """
        available = []
        for i in range(max_index):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available


# Backward compatibility alias
USBCamera = Camera
