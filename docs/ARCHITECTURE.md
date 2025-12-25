# System Architecture

## Overview

The Pipeline Inspection System is a dual-platform AI-powered defect detection solution designed for both **demonstration** (MacBook Pro) and **production deployment** (ARM + NPU edge devices).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PIPELINE INSPECTION SYSTEM                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐                    ┌──────────────────────┐
│                  │                    │                      │
│  USB CAMERA      │◄──────USB─────────►│   HOST DEVICE        │
│  (Pipeline)      │                    │                      │
│                  │                    │  ┌────────────────┐  │
│  - 640x480       │                    │  │   BACKEND      │  │
│  - 30 FPS        │                    │  │   (Python)     │  │
│  - MJPG/YUYV     │                    │  │                │  │
└──────────────────┘                    │  │  • FastAPI     │  │
                                        │  │  • YOLO        │  │
                                        │  │  • OpenCV      │  │
                                        │  │  • TFLite      │  │
                                        │  └────────┬───────┘  │
                                        │           │          │
                                        │      WebSocket       │
                                        │           │          │
                                        │  ┌────────▼───────┐  │
                                        │  │   FRONTEND     │  │
                                        │  │   (Next.js)    │  │
                                        │  │                │  │
                                        │  │  • Dashboard   │  │
                                        │  │  • Video View  │  │
                                        │  │  • Reports     │  │
                                        │  └────────────────┘  │
                                        │                      │
                                        │  MacBook / PC / ARM  │
                                        └──────────────────────┘
                                                    │
                                                    │ HTTP
                                                    ▼
                                        ┌──────────────────────┐
                                        │   CLIENT BROWSER     │
                                        │   localhost:3000     │
                                        └──────────────────────┘
```

## Deployment Scenarios

### Scenario 1: MacBook Pro Demo

```
┌─────────────────────────────────────────────────────┐
│                  MacBook Pro                        │
│  ┌──────────────┐          ┌──────────────┐        │
│  │   Backend    │◄────────►│   Frontend   │        │
│  │   Port 8000  │ WebSocket│   Port 3000  │        │
│  └──────┬───────┘          └──────────────┘        │
│         │                                           │
│         ▼                                           │
│  ┌──────────────┐                                  │
│  │ YOLO (FP32)  │                                  │
│  │ CPU/Metal    │  15-30 FPS                       │
│  └──────────────┘                                  │
└──────────────┬──────────────────────────────────────┘
               │
               │ USB
               ▼
         ┌──────────┐
         │  Camera  │
         └──────────┘
```

**Performance:**
- Apple Silicon (M1/M2/M3): 15-30 FPS ⭐
- Intel Mac: 8-18 FPS
- Perfect for demos and development

---

### Scenario 2: Intel PC Development

```
┌─────────────────────────────────────────────────────┐
│                  Intel/AMD PC                       │
│  ┌──────────────┐          ┌──────────────┐        │
│  │   Backend    │◄────────►│   Frontend   │        │
│  │   Port 8000  │ WebSocket│   Port 3000  │        │
│  └──────┬───────┘          └──────────────┘        │
│         │                                           │
│         ▼                                           │
│  ┌──────────────┐                                  │
│  │ YOLO (FP32)  │                                  │
│  │ CPU Only     │  5-15 FPS                        │
│  └──────────────┘                                  │
└──────────────┬──────────────────────────────────────┘
               │
               │ USB
               ▼
         ┌──────────┐
         │  Camera  │
         └──────────┘
```

**Performance:**
- i5/i7: 8-15 FPS
- Good for development and testing

---

### Scenario 3: ARM + NPU Production ⭐

```
┌─────────────────────────────────────────────────────┐
│            ARM Edge Device (Production)             │
│                                                     │
│  ┌──────────────┐          ┌──────────────┐        │
│  │   Backend    │◄────────►│   Frontend   │        │
│  │   Port 8000  │ WebSocket│   Port 3000  │        │
│  └──────┬───────┘          └──────────────┘        │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────────────────────┐              │
│  │    YOLO INT8 Quantized Model     │              │
│  │                                  │              │
│  │  ┌────────────┐  ┌────────────┐ │              │
│  │  │  TFLite    │  │ NPU        │ │              │
│  │  │  Runtime   │─►│ Delegate   │ │              │
│  │  └────────────┘  └─────┬──────┘ │              │
│  │                        │        │              │
│  │                        ▼        │              │
│  │                  ┌──────────┐   │              │
│  │                  │   NPU    │   │              │
│  │                  │ 6 TOPS   │   │  30-60 FPS   │
│  │                  └──────────┘   │              │
│  └──────────────────────────────────┘              │
│                                                     │
│  RK3588 / A311D / MT8395                           │
│  ARM Cortex-A55/A76                                │
│  Power: 5-8W                                       │
└──────────────┬──────────────────────────────────────┘
               │
               │ USB
               ▼
         ┌──────────┐
         │  Camera  │
         └──────────┘
```

**Performance:**
- 30-60 FPS (NPU accelerated)
- < 50ms latency
- 5-8W power consumption
- Production deployment

---

## Data Flow

### 1. Video Capture Flow

```
USB Camera
    │
    │ Frame Capture (30 FPS)
    ▼
OpenCV (backend/camera.py)
    │
    │ Read Frame (640x480 BGR)
    ▼
YOLO Detector (backend/yolo_detector.py)
    │
    ├─► Preprocess (resize, normalize)
    │
    ├─► Inference (YOLO model)
    │   │
    │   ├─► FP32 (MacBook/PC): PyTorch
    │   └─► INT8 (ARM+NPU): TFLite + NPU
    │
    ├─► Postprocess (NMS, filtering)
    │
    └─► Detections [{class, conf, bbox}, ...]
         │
         ▼
Draw Annotations (bounding boxes)
         │
         ▼
Encode to JPEG + Base64
         │
         ▼
WebSocket Send (backend/app.py)
         │
         │ {"frame": "base64...", "detections": [...]}
         ▼
Frontend (components/VideoStream.tsx)
         │
         ├─► Decode Base64
         ├─► Display on Canvas
         └─► Update Detection Log
```

### 2. Detection Processing Flow

```
Detections
    │
    ├─► Real-time Display
    │   └─► Frontend Dashboard
    │
    ├─► History Storage
    │   └─► Backend Memory (detector.detections_history)
    │
    └─► Report Generation
        │
        ├─► PDF Generation (report_generator.py)
        │   ├─► ReportLab
        │   ├─► Summary Statistics
        │   ├─► Detection Table
        │   └─► Output: inspection_report_YYYYMMDD.pdf
        │
        └─► JSON Export
            ├─► Structured Data
            ├─► Metadata
            └─► Output: inspection_report_YYYYMMDD.json
```

---

## Component Architecture

### Backend (Python + FastAPI)

```
backend/
│
├─ app.py                    # Main FastAPI application
│  ├─ REST API endpoints     # /api/system/status, /api/camera/*, etc.
│  ├─ WebSocket endpoint     # /ws/video (real-time streaming)
│  └─ CORS middleware        # Allow frontend access
│
├─ camera.py                 # USB Camera interface
│  ├─ USBCamera class        # OpenCV wrapper
│  ├─ read_frame()           # Capture frames
│  └─ list_cameras()         # Device detection
│
├─ yolo_detector.py          # YOLO detection engine
│  ├─ PipelineDefectDetector # Detection class
│  ├─ load_model()           # Load YOLO (PyTorch or TFLite)
│  ├─ detect()               # Run inference
│  ├─ draw_detections()      # Annotate frames
│  └─ detections_history[]   # Store all detections
│
├─ report_generator.py       # Report generation
│  ├─ generate_pdf()         # PDF reports (ReportLab)
│  ├─ generate_json()        # JSON export
│  └─ InspectionMetadata     # Report metadata
│
└─ config.py                 # Configuration management
   ├─ Settings (Pydantic)    # Type-safe config
   └─ .env loading           # Environment variables
```

### Frontend (Next.js + React)

```
frontend/
│
├─ app/
│  ├─ page.tsx               # Main dashboard page
│  └─ layout.tsx             # Root layout + metadata
│
├─ components/
│  │
│  ├─ VideoStream.tsx        # Live video component
│  │  ├─ WebSocket client    # Connect to backend
│  │  ├─ Canvas rendering    # Display video + boxes
│  │  └─ FPS counter         # Performance monitoring
│  │
│  ├─ DetectionLog.tsx       # Detection history
│  │  ├─ Real-time updates   # New detections
│  │  ├─ Scrollable list     # Auto-scroll to latest
│  │  └─ Statistics          # Count, avg confidence
│  │
│  ├─ SystemStatus.tsx       # System info widget
│  │  ├─ Camera status       # Resolution, FPS
│  │  ├─ Detector status     # Model, threshold
│  │  └─ Detection stats     # Total, by class
│  │
│  └─ ReportGenerator.tsx    # Report creation UI
│     ├─ Metadata form       # Location, inspector, notes
│     ├─ Format selection    # PDF, JSON, or both
│     └─ Download trigger    # Generate and download
│
└─ types/
   └─ index.ts               # TypeScript definitions
      ├─ Detection           # Detection object
      ├─ SystemStatus        # System state
      └─ InspectionMetadata  # Report metadata
```

---

## Model Pipeline

### Development (MacBook/PC)

```
┌────────────────────────────────────────────┐
│  1. Data Collection & Labeling             │
│     • Collect pipeline images (500-1000)   │
│     • Label defects (Roboflow/LabelImg)    │
│     • Export YOLO format                   │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│  2. Model Training                         │
│     • Platform: PC/Cloud with GPU          │
│     • Framework: Ultralytics YOLO          │
│     • Output: best.pt (PyTorch weights)    │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│  3. Model Export (Demo)                    │
│     • Format: PyTorch (.pt)                │
│     • Deployment: MacBook/PC               │
│     • Performance: 15-30 FPS               │
└────────────────────────────────────────────┘
```

### Production (ARM + NPU)

```
best.pt (PyTorch)
     │
     │ Export to ONNX
     ▼
model.onnx
     │
     │ Convert to TensorFlow
     ▼
saved_model/ (TensorFlow)
     │
     │ Convert to TFLite
     ▼
model_fp32.tflite
     │
     │ INT8 Quantization
     │ • Calibration data (100-300 images)
     │ • Post-training quantization
     ▼
model_int8.tflite
     │
     │ NPU Delegate Integration
     ▼
Deployed on ARM + NPU
     │
     └─► 30-60 FPS @ 5-8W
```

---

## Network Communication

### WebSocket Protocol

**Endpoint:** `ws://localhost:8000/ws/video`

**Message Format (Backend → Frontend):**
```json
{
  "frame": "base64_encoded_jpeg_image",
  "detections": [
    {
      "class_name": "crack",
      "confidence": 0.87,
      "bbox": {
        "x1": 120,
        "y1": 200,
        "x2": 340,
        "y2": 280
      },
      "timestamp": "2025-01-24T14:28:15.123456",
      "frame_position": 3.5
    }
  ],
  "timestamp": "2025-01-24T14:28:15.123456"
}
```

**Frame Rate:** 30 FPS max (controlled by backend)

**Automatic Reconnection:** Frontend retries every 3 seconds on disconnect

---

## REST API Endpoints

### System Management
- `GET /` - Health check
- `GET /api/system/status` - System status (camera, detector, stats)
- `GET /api/cameras/list` - List available cameras

### Camera Control
- `POST /api/camera/start` - Start camera
- `POST /api/camera/stop` - Stop camera

### Detection Management
- `GET /api/detections/history?limit=100` - Get detection history
- `DELETE /api/detections/clear` - Clear detection history

### Report Generation
- `POST /api/report/generate` - Generate inspection report
- `GET /api/report/download/{report_id}?format=pdf` - Download report
- `GET /api/reports/list` - List all reports

---

## Security & Performance

### Security Considerations

1. **CORS Configuration**
   - Allowed origins: `localhost:3000`, `127.0.0.1:3000`
   - Production: Configure with actual domain

2. **Camera Permissions**
   - macOS: System Preferences → Privacy → Camera
   - Linux: User must be in `video` group

3. **File Access**
   - Reports directory: Configurable path
   - Models directory: Read-only access recommended

### Performance Optimization

1. **Video Streaming**
   - JPEG compression for WebSocket
   - Frame rate limiting (30 FPS max)
   - Base64 encoding for web compatibility

2. **Model Inference**
   - Batch size: 1 (real-time priority)
   - Input size: 640x640 (configurable)
   - Confidence threshold: 0.5 (adjustable)

3. **NPU Optimization (ARM)**
   - INT8 quantization (4x smaller, 3-5x faster)
   - NPU delegate (hardware acceleration)
   - XNNPACK fallback (CPU optimization)

---

## Scalability

### Single Device
- 1 camera → 1 backend instance → 1 frontend
- Suitable for: Demos, development, single inspection point

### Multiple Devices (Future)
- Multiple cameras → Multiple backend instances → Load balancer
- Centralized report storage
- Database integration for historical analysis

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Hardware** | USB Camera | Video capture |
| **Hardware** | ARM + NPU / MacBook / PC | Compute platform |
| **Backend** | Python 3.8+ | Application logic |
| **Web Framework** | FastAPI | REST API + WebSocket |
| **Video** | OpenCV | Camera interface |
| **AI Model** | YOLO (Ultralytics) | Object detection |
| **Inference** | PyTorch / TFLite | Model execution |
| **Reports** | ReportLab | PDF generation |
| **Frontend** | Next.js 15 | Web application |
| **UI Framework** | React | Component system |
| **Styling** | Tailwind CSS | Responsive design |
| **Type Safety** | TypeScript | Development quality |
| **Communication** | WebSocket | Real-time updates |

---

## Deployment Comparison Matrix

| Aspect | MacBook Demo | Intel PC Dev | ARM+NPU Production |
|--------|--------------|--------------|-------------------|
| **Hardware** | MacBook Pro | PC/NUC | SBC (RK3588, etc.) |
| **CPU** | Apple M1/M2/M3 or Intel | Intel/AMD | ARM Cortex-A55/A76 |
| **Accelerator** | Metal GPU | None | NPU (6 TOPS) |
| **Model Format** | PyTorch (.pt) | PyTorch (.pt) | TFLite INT8 (.tflite) |
| **Framework** | Ultralytics YOLO | Ultralytics YOLO | TFLite + NPU Delegate |
| **FPS** | 15-30 (M-series) / 8-18 (Intel) | 5-15 | 30-60 |
| **Latency** | 45-60ms / 100ms | 150ms | < 50ms |
| **Power** | 10-15W / 15-25W | 15-25W | 5-8W |
| **Cost** | $0 (existing) | $800-1500 | $300-600 |
| **Form Factor** | Laptop (portable) | Desktop (fixed) | Compact SBC (mountable) |
| **Use Case** | **Demos, Development** | Development, Training | **Production Deployment** |

---

This architecture provides **flexibility** (3 deployment options), **performance** (up to 60 FPS), and **cost-effectiveness** (~75% savings with ARM+NPU).
