"""
FastAPI application for Pipeline Inspection System
Provides REST API and WebSocket endpoints for real-time video streaming
"""
import asyncio
import base64
import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import cv2
import numpy as np

from config import settings
from camera import USBCamera
from yolo_detector import PipelineDefectDetector, Detection
from report_generator import InspectionReportGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pipeline Inspection System",
    description="Real-time pipeline defect detection using YOLO",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
camera = USBCamera()
detector = PipelineDefectDetector()
report_generator = InspectionReportGenerator()

# Active WebSocket connections
active_connections: List[WebSocket] = []


# Pydantic models
class InspectionMetadata(BaseModel):
    location: str = "Unknown"
    inspector: str = "System"
    notes: str = ""


class ReportRequest(BaseModel):
    metadata: InspectionMetadata
    format: str = "both"  # "pdf", "json", or "both"


class DetectionResponse(BaseModel):
    class_name: str
    confidence: float
    bbox: Dict[str, int]
    timestamp: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting Pipeline Inspection System...")

    # Load YOLO model
    if detector.load_model():
        logger.info("✓ YOLO model loaded successfully")
    else:
        logger.error("✗ Failed to load YOLO model")

    # List available cameras
    available_cameras = USBCamera.list_available_cameras()
    logger.info(f"Available cameras: {available_cameras}")

    logger.info("System ready!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    camera.close()


# Health check
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Pipeline Inspection System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/system/status")
async def system_status():
    """Get system status"""
    return {
        "camera": {
            "is_opened": camera.is_opened,
            "index": camera.camera_index,
            "resolution": f"{camera.width}x{camera.height}",
            "fps": camera.fps
        },
        "detector": {
            "is_loaded": detector.is_loaded,
            "model_path": detector.model_path,
            "confidence_threshold": detector.confidence_threshold
        },
        "detections": {
            "total": len(detector.detections_history),
            "summary": detector.get_detection_summary()
        }
    }


@app.get("/api/cameras/list")
async def list_cameras():
    """List available cameras"""
    available = USBCamera.list_available_cameras(max_index=5)
    return {
        "available_cameras": available,
        "current_camera": camera.camera_index
    }


@app.post("/api/camera/start")
async def start_camera():
    """Start camera"""
    if camera.is_opened:
        return {"message": "Camera already started", "status": "running"}

    if camera.open():
        return {"message": "Camera started successfully", "status": "running"}
    else:
        raise HTTPException(status_code=500, detail="Failed to start camera")


@app.post("/api/camera/stop")
async def stop_camera():
    """Stop camera"""
    camera.close()
    return {"message": "Camera stopped", "status": "stopped"}


@app.get("/api/detections/history")
async def get_detection_history(limit: int = 100):
    """Get detection history"""
    history = detector.detections_history[-limit:]
    return {
        "total": len(detector.detections_history),
        "returned": len(history),
        "detections": [det.to_dict() for det in history]
    }


@app.delete("/api/detections/clear")
async def clear_detections():
    """Clear detection history"""
    detector.clear_history()
    return {"message": "Detection history cleared"}


@app.post("/api/report/generate")
async def generate_report(request: ReportRequest):
    """Generate inspection report"""
    if not detector.detections_history:
        raise HTTPException(
            status_code=400,
            detail="No detections available for report generation"
        )

    metadata_dict = request.metadata.dict()

    try:
        report_files = report_generator.generate_report(
            detections=detector.detections_history,
            inspection_metadata=metadata_dict,
            format=request.format
        )

        return {
            "message": "Report generated successfully",
            "files": report_files
        }

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/download/{report_id}")
async def download_report(report_id: str, format: str = "pdf"):
    """Download report file"""
    reports_dir = Path(settings.REPORTS_DIR)
    filename = f"inspection_report_{report_id}.{format}"
    filepath = reports_dir / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type="application/pdf" if format == "pdf" else "application/json"
    )


@app.get("/api/reports/list")
async def list_reports():
    """List all available reports"""
    reports_dir = Path(settings.REPORTS_DIR)

    if not reports_dir.exists():
        return {"reports": []}

    reports = []
    for file in reports_dir.glob("inspection_report_*"):
        reports.append({
            "filename": file.name,
            "created": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
            "size": file.stat().st_size
        })

    return {"reports": sorted(reports, key=lambda x: x["created"], reverse=True)}


# WebSocket endpoint for real-time video streaming
@app.websocket("/ws/video")
async def websocket_video_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time video streaming with detection
    """
    await websocket.accept()
    active_connections.append(websocket)

    logger.info(f"WebSocket connected. Active connections: {len(active_connections)}")

    # Open camera if not already open
    if not camera.is_opened:
        if not camera.open():
            await websocket.send_json({"error": "Failed to open camera"})
            await websocket.close()
            return

    try:
        while True:
            # Read frame
            ret, frame = camera.read_frame()

            if not ret or frame is None:
                await websocket.send_json({"error": "Failed to read frame"})
                await asyncio.sleep(0.1)
                continue

            # Perform detection
            detections = detector.detect(frame)

            # Draw detections on frame
            annotated_frame = detector.draw_detections(frame, detections)

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame)

            if not ret:
                continue

            # Encode to base64
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Send frame and detections
            await websocket.send_json({
                "frame": frame_base64,
                "detections": [det.to_dict() for det in detections],
                "timestamp": datetime.now().isoformat()
            })

            # Control frame rate (30 FPS max)
            await asyncio.sleep(1 / 30)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        active_connections.remove(websocket)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
