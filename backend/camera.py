"""
USB Camera interface for pipeline inspection
Handles video capture from USB camera module
"""
import cv2
import numpy as np
from typing import Optional, Tuple
import logging
from config import settings

logger = logging.getLogger(__name__)


class USBCamera:
    """USB Camera capture and management"""

    def __init__(
        self,
        camera_index: int = None,
        width: int = None,
        height: int = None,
        fps: int = None
    ):
        """
        Initialize USB camera

        Args:
            camera_index: Camera device index (default from settings)
            width: Frame width (default from settings)
            height: Frame height (default from settings)
            fps: Target FPS (default from settings)
        """
        self.camera_index = camera_index or settings.CAMERA_INDEX
        self.width = width or settings.CAMERA_WIDTH
        self.height = height or settings.CAMERA_HEIGHT
        self.fps = fps or settings.CAMERA_FPS

        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False

    def open(self) -> bool:
        """
        Open camera connection

        Returns:
            bool: True if camera opened successfully
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                logger.error(f"Failed to open camera at index {self.camera_index}")
                return False

            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

            # Verify settings
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))

            logger.info(
                f"Camera opened: {actual_width}x{actual_height} @ {actual_fps}fps"
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
        List available camera indices

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
