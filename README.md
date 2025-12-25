# Pipeline Inspection System

AI-powered real-time pipeline defect detection system using YOLO and TensorFlow Lite. This system captures video from a USB camera, detects pipeline defects (cracks, rust, foreign objects, etc.), and generates comprehensive inspection reports.

**📖 [View Detailed Architecture Documentation](docs/ARCHITECTURE.md)**

## Features

- 🎥 **Real-time Video Processing** - Live video stream from USB camera with WebSocket
- 🤖 **AI-Powered Detection** - YOLO-based defect detection (foreign objects, cracks, rust, corrosion, sediment, leaks)
- 📊 **Interactive Dashboard** - Modern web interface with live detection visualization
- 📄 **Report Generation** - Automated PDF and JSON reports with detailed findings
- 🚀 **Dual Deployment Options**:
  - **Intel/PC** - CPU-only deployment (5-15 FPS)
  - **ARM + NPU** - Edge device with NPU acceleration (30-60 FPS) ⭐ **Recommended for production**
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 💰 **Cost-Effective** - ARM deployment: ~60% lower hardware cost, ~70% lower power consumption

## System Architecture

```
┌─────────────────┐      USB       ┌──────────────────┐
│  USB Camera     │────────────────▶│  Intel Host PC   │
│  (Pipeline)     │                 │                  │
└─────────────────┘                 │  ┌────────────┐  │
                                    │  │  Backend   │  │
                                    │  │  (Python)  │  │
                                    │  │            │  │
                                    │  │  - FastAPI │  │
                                    │  │  - YOLO    │  │
                                    │  │  - OpenCV  │  │
                                    │  └─────┬──────┘  │
                                    │        │         │
                                    │        │ WebSocket
                                    │        │         │
                                    │  ┌─────▼──────┐  │
                                    │  │  Frontend  │  │
                                    │  │  (Next.js) │  │
                                    │  └────────────┘  │
                                    └──────────────────┘
```

## Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - High-performance web framework
- **OpenCV** - Video capture and processing
- **Ultralytics YOLO** - Object detection
- **TensorFlow / TensorFlow Lite** - Model inference
- **ReportLab** - PDF report generation

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **WebSocket** - Real-time communication

## Deployment Options

This system supports **three deployment platforms**:

### 🍎 MacBook Pro (Demos & Development) 💼
- **Best for**: Client demos, presentations, development
- **Hardware**: MacBook Pro (Intel or Apple Silicon M1/M2/M3)
- **Performance**:
  - Intel: 8-18 FPS
  - Apple Silicon: 15-30 FPS ⭐ **Best demo experience**
- **Setup time**: ~10 minutes
- **Cost**: $0 (use existing MacBook)
- **See**: [macOS Setup Guide](deployment/macos/README_MACOS.md)

**Quick Start on macOS:**
```bash
cd /Users/wlin/dev/pipeline-inspection
./start_macos.sh
```

### 🖥️ Intel/PC (Development & Testing)
- **Best for**: Development, testing, model training
- **Hardware**: Any Intel/AMD PC with USB camera
- **Performance**: 5-15 FPS (CPU-only)
- **Setup time**: ~15 minutes
- **Cost**: $800-1500 (if purchasing new)
- **See**: Standard installation below

### ⚡ ARM + NPU (Production) ⭐ **Recommended for Deployment**
- **Best for**: Production deployment, edge devices, field installation
- **Hardware**: ARM64 device with 6+ TOPS NPU (e.g., RK3588, A311D)
- **Performance**: 30-60 FPS (NPU-accelerated)
- **Power**: 5-8W (vs 15-30W on Intel/Mac)
- **Cost**: ~$300-600 per unit
- **Setup time**: ~10 minutes for FP32 testing, 2-3 weeks for full NPU optimization
- **See**: [ARM Deployment Guide](deployment/arm/README_ARM.md) | [Quick Start](deployment/arm/QUICKSTART_ARM.md)

### Performance Comparison

| Platform | FPS | Latency | Power | Cost | Best For |
|----------|-----|---------|-------|------|----------|
| **MacBook (Intel)** | 8-18 | ~100ms | 15-25W | $0* | Demos |
| **MacBook (M1/M2/M3)** | 15-30 | ~50ms | 10-15W | $0* | **Demos** ⭐ |
| **Intel PC** | 5-15 | ~150ms | 15-25W | $800+ | Dev/Test |
| **ARM CPU (FP32)** | 5-8 | ~180ms | 8-12W | $300-600 | Testing |
| **ARM NPU (INT8)** | **30-60** | **< 50ms** | **5-8W** | **$300-600** | **Production** ⭐ |

*Using existing hardware

### Typical Workflow

```
1. Development     → MacBook Pro / PC
   ├─ Write code
   ├─ Train models
   └─ Test features

2. Client Demos    → MacBook Pro (M1/M2/M3 recommended)
   ├─ Live demonstrations
   ├─ Show real-time detection
   └─ Generate sample reports

3. Production      → ARM + NPU Edge Device
   ├─ Field deployment
   ├─ 24/7 operation
   └─ Maximum efficiency
```

---

## Quick Start

### 🍎 MacBook Pro (Recommended for Demos)

**One-command setup:**
```bash
cd /Users/wlin/dev/pipeline-inspection
./start_macos.sh
```

**Access:** http://localhost:3000

**See:** [macOS Setup Guide](deployment/macos/README_MACOS.md)

---

## Installation (Intel/PC - Development)

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- USB Camera
- Intel/AMD CPU (GPU optional)

**For ARM production deployment**, see [ARM Quick Start Guide](deployment/arm/QUICKSTART_ARM.md)

**For macOS demos**, see [macOS Setup Guide](deployment/macos/README_MACOS.md)

### 1. Clone the Repository

```bash
cd /Users/wlin/dev
cd pipeline-inspection
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env if needed (camera index, thresholds, etc.)
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Build the application
npm run build
```

## Usage

### Starting the System

#### Terminal 1 - Start Backend

```bash
cd backend
source venv/bin/activate  # Activate venv
python app.py
```

The backend will start at `http://localhost:8000`

#### Terminal 2 - Start Frontend

```bash
cd frontend
npm run dev
```

The frontend will start at `http://localhost:3000`

### Accessing the System

1. Open your browser and navigate to `http://localhost:3000`
2. The system will automatically connect to the camera
3. Real-time detection will start immediately
4. View detections in the Detection Log
5. Generate reports when inspection is complete

## Configuration

### Backend Configuration (`backend/.env`)

```env
# Camera Settings
CAMERA_INDEX=0          # USB camera index (0 for first camera)
CAMERA_WIDTH=640        # Video resolution width
CAMERA_HEIGHT=480       # Video resolution height
CAMERA_FPS=30           # Target frames per second

# Model Settings
MODEL_PATH=../models/yolov8n.pt
CONFIDENCE_THRESHOLD=0.5    # Detection confidence threshold (0.0-1.0)
IOU_THRESHOLD=0.45          # Non-maximum suppression threshold

# Detection Classes (customize for your pipeline defects)
DEFECT_CLASSES=foreign_object,crack,rust,corrosion,sediment,leak
```

### Finding Your Camera Index

```bash
# List available cameras
cd backend
source venv/bin/activate
python -c "from camera import USBCamera; print(USBCamera.list_available_cameras())"
```

## Training Custom Model

The system ships with a demo YOLOv8 model. For pipeline-specific detection, you need to train a custom model:

### 1. Prepare Dataset

```
dataset/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

### 2. Label Your Data

Use tools like:
- [Roboflow](https://roboflow.com)
- [LabelImg](https://github.com/tzutalin/labelImg)
- [CVAT](https://github.com/opencv/cvat)

Classes to label:
- `foreign_object` - Foreign objects in pipeline
- `crack` - Cracks and fissures
- `rust` - Rust and oxidation
- `corrosion` - Corrosion damage
- `sediment` - Sediment buildup
- `leak` - Leaks and water damage

### 3. Train YOLO Model

```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolov8n.pt')

# Train on your dataset
results = model.train(
    data='dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='pipeline_defect_detector'
)

# Export to TensorFlow Lite for deployment
model.export(format='tflite')
```

### 4. Deploy Your Model

```bash
# Copy trained model to models directory
cp runs/detect/pipeline_defect_detector/weights/best.pt ../models/pipeline_v1.pt

# Update .env
MODEL_PATH=../models/pipeline_v1.pt
```

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### System Status
```bash
GET /api/system/status
```

#### Start Camera
```bash
POST /api/camera/start
```

#### Generate Report
```bash
POST /api/report/generate
Content-Type: application/json

{
  "metadata": {
    "location": "Building A - Basement",
    "inspector": "John Doe",
    "notes": "Routine inspection"
  },
  "format": "both"
}
```

#### Download Report
```bash
GET /api/report/download/{report_id}?format=pdf
```

## Report Examples

### PDF Report
- Executive summary with inspection details
- Detection statistics by defect type
- Detailed findings table with timestamps
- Severity classification
- Professional formatting

### JSON Report
```json
{
  "metadata": {
    "report_id": "20250124_143022",
    "timestamp": "2025-01-24T14:30:22",
    "location": "Building A",
    "total_detections": 15
  },
  "detections": [
    {
      "class_name": "crack",
      "confidence": 0.87,
      "bbox": {"x1": 120, "y1": 200, "x2": 340, "y2": 280},
      "timestamp": "2025-01-24T14:28:15",
      "frame_position": 3.5
    }
  ],
  "summary": {
    "total_detections": 15,
    "by_class": {"crack": 5, "rust": 10},
    "average_confidence": 0.82
  }
}
```

## Performance

### CPU-Only Performance (Intel i5/i7)
- **Resolution**: 640x640
- **FPS**: 8-20 FPS
- **Latency**: < 150ms
- **CPU Usage**: 40-60%

### Optimization Tips

1. **Lower Resolution** - Use 320x320 for faster processing
2. **Increase Threshold** - Higher confidence threshold = fewer false positives
3. **Use TFLite** - Export to TensorFlow Lite for 2-3x speedup
4. **Batch Processing** - Process video files offline for higher accuracy

## Troubleshooting

### Camera Not Found

```bash
# Check camera permissions (macOS)
# System Settings > Privacy & Security > Camera

# List available cameras
python -c "from camera import USBCamera; print(USBCamera.list_available_cameras())"

# Try different camera index in .env
CAMERA_INDEX=1
```

### WebSocket Connection Failed

```bash
# Ensure backend is running
curl http://localhost:8000

# Check CORS settings in backend/app.py
# Verify frontend URL is allowed
```

### Low FPS

```bash
# Reduce resolution
CAMERA_WIDTH=320
CAMERA_HEIGHT=240

# Increase confidence threshold
CONFIDENCE_THRESHOLD=0.6

# Export model to TFLite
python -c "from yolo_detector import PipelineDefectDetector; d = PipelineDefectDetector(); d.load_model(); d.export_to_tflite()"
```

### Model Download Issues

The system will automatically download YOLOv8n on first run. If download fails:

```bash
# Manual download
cd models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

## Project Structure

```
pipeline-inspection/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── camera.py              # USB camera interface
│   ├── yolo_detector.py       # YOLO detection logic
│   ├── report_generator.py    # PDF/JSON report generation
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main page
│   │   └── layout.tsx         # Root layout
│   ├── components/
│   │   ├── VideoStream.tsx    # Live video component
│   │   ├── DetectionLog.tsx   # Detection history
│   │   ├── SystemStatus.tsx   # System info
│   │   └── ReportGenerator.tsx # Report UI
│   ├── types/
│   │   └── index.ts           # TypeScript types
│   └── package.json
├── models/                     # YOLO models
├── reports/                    # Generated reports
└── README.md
```

## Future Enhancements

- [ ] Multi-camera support
- [ ] Real-time distance measurement
- [ ] 3D pipeline mapping
- [ ] Mobile app (React Native)
- [ ] Cloud deployment
- [ ] Historical trend analysis
- [ ] Email/SMS alerts for critical defects
- [ ] Integration with maintenance systems

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Email: support@pipeline-inspection.com

## Credits

- **YOLO**: [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- **FastAPI**: [FastAPI Framework](https://fastapi.tiangolo.com)
- **Next.js**: [Next.js by Vercel](https://nextjs.org)

---

**Built with ❤️ for pipeline safety and maintenance**
