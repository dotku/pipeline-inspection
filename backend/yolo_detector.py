"""
YOLO-based defect detection for pipeline inspection
Supports both PyTorch YOLO and TensorFlow Lite deployment
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path

from ultralytics import YOLO
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Single detection result"""
    class_name: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    timestamp: datetime
    frame_position: Optional[float] = None  # Position in pipeline (meters)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "class_name": self.class_name,
            "confidence": float(self.confidence),
            "bbox": {
                "x1": int(self.bbox[0]),
                "y1": int(self.bbox[1]),
                "x2": int(self.bbox[2]),
                "y2": int(self.bbox[3])
            },
            "timestamp": self.timestamp.isoformat(),
            "frame_position": self.frame_position
        }


class PipelineDefectDetector:
    """
    YOLO-based pipeline defect detector
    Detects: foreign objects, cracks, rust, corrosion, sediment, leaks
    """

    def __init__(
        self,
        model_path: str = None,
        confidence_threshold: float = None,
        iou_threshold: float = None
    ):
        """
        Initialize defect detector

        Args:
            model_path: Path to YOLO model (.pt or .tflite)
            confidence_threshold: Minimum confidence for detections
            iou_threshold: IOU threshold for NMS
        """
        self.model_path = model_path or settings.MODEL_PATH
        self.confidence_threshold = confidence_threshold or settings.CONFIDENCE_THRESHOLD
        self.iou_threshold = iou_threshold or settings.IOU_THRESHOLD

        self.model: Optional[YOLO] = None
        self.is_loaded = False

        # Detection history
        self.detections_history: List[Detection] = []

    def load_model(self) -> bool:
        """
        Load YOLO model

        Returns:
            bool: True if model loaded successfully
        """
        try:
            model_path = Path(self.model_path)

            if not model_path.exists():
                logger.warning(
                    f"Model not found at {self.model_path}. "
                    f"Downloading YOLOv8n as demo model..."
                )
                # Download YOLOv8n as demo (will be replaced with custom trained model)
                self.model = YOLO("yolov8n.pt")
                logger.info("Demo model (YOLOv8n) loaded successfully")
            else:
                self.model = YOLO(str(model_path))
                logger.info(f"Model loaded from {self.model_path}")

            self.is_loaded = True
            return True

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def detect(
        self,
        frame: np.ndarray,
        frame_position: Optional[float] = None
    ) -> List[Detection]:
        """
        Perform detection on a single frame

        Args:
            frame: Input image (BGR format)
            frame_position: Position in pipeline (meters) for reporting

        Returns:
            List of Detection objects
        """
        if not self.is_loaded or self.model is None:
            logger.warning("Model not loaded")
            return []

        try:
            # Run inference
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )

            detections = []
            timestamp = datetime.now()

            # Parse results
            for result in results:
                boxes = result.boxes

                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    # Get class and confidence
                    class_id = int(box.cls[0].cpu().numpy())
                    confidence = float(box.conf[0].cpu().numpy())

                    # Get class name
                    class_name = result.names[class_id]

                    detection = Detection(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(x1, y1, x2, y2),
                        timestamp=timestamp,
                        frame_position=frame_position
                    )

                    detections.append(detection)

            # Add to history
            self.detections_history.extend(detections)

            return detections

        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return []

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Detection]
    ) -> np.ndarray:
        """
        Draw detection boxes on frame

        Args:
            frame: Input image
            detections: List of detections to draw

        Returns:
            Annotated image
        """
        annotated_frame = frame.copy()

        # Color map for different defect types
        color_map = {
            "foreign_object": (0, 0, 255),      # Red
            "crack": (0, 165, 255),             # Orange
            "rust": (0, 140, 255),              # Dark Orange
            "corrosion": (0, 255, 255),         # Yellow
            "sediment": (139, 69, 19),          # Brown
            "leak": (255, 0, 0),                # Blue
        }

        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)

            # Get color (default to green for unknown classes)
            color = color_map.get(det.class_name.lower(), (0, 255, 0))

            # Draw box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{det.class_name}: {det.confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

            # Draw label background
            cv2.rectangle(
                annotated_frame,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1
            )

            # Draw label text
            cv2.putText(
                annotated_frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

        return annotated_frame

    def get_detection_summary(self) -> Dict[str, Any]:
        """
        Get summary of all detections

        Returns:
            Dictionary with detection statistics
        """
        if not self.detections_history:
            return {
                "total_detections": 0,
                "by_class": {},
                "average_confidence": 0.0
            }

        # Count by class
        by_class = {}
        total_confidence = 0.0

        for det in self.detections_history:
            by_class[det.class_name] = by_class.get(det.class_name, 0) + 1
            total_confidence += det.confidence

        return {
            "total_detections": len(self.detections_history),
            "by_class": by_class,
            "average_confidence": total_confidence / len(self.detections_history)
        }

    def clear_history(self):
        """Clear detection history"""
        self.detections_history.clear()
        logger.info("Detection history cleared")

    def export_to_tflite(self, output_path: str = "../models/yolov8n.tflite"):
        """
        Export current model to TensorFlow Lite format

        Args:
            output_path: Path to save .tflite model
        """
        if not self.is_loaded or self.model is None:
            logger.error("Model not loaded, cannot export")
            return False

        try:
            # Export to TFLite
            self.model.export(format="tflite", imgsz=640)
            logger.info(f"Model exported to TFLite: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to TFLite: {e}")
            return False
