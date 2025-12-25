# ARM Deployment - Quick Start Guide

Get your Pipeline Inspection System running on ARM in **10 minutes**.

## Prerequisites

- ARM device with USB camera
- Linux OS (Ubuntu/Debian recommended)
- Internet connection (for initial setup)

## Step 1: Setup Environment (5 min)

```bash
# SSH into your ARM device
ssh user@arm-device-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv git
sudo apt install -y libopencv-dev v4l-utils

# Clone project (or transfer files)
# Assuming you've already created the project on your PC
```

## Step 2: Install Python Dependencies (3 min)

```bash
cd /path/to/pipeline-inspection/deployment/arm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install ARM-optimized packages
pip install -r requirements_arm.txt

# Verify installation
python -c "import tflite_runtime; print('✓ TFLite ready')"
python -c "import cv2; print('✓ OpenCV ready')"
```

## Step 3: Convert Model to TFLite (2 min)

**Option A: On ARM Device** (if sufficient RAM)
```bash
cd /path/to/pipeline-inspection

# Install ultralytics temporarily
pip install ultralytics

# Convert YOLO to TFLite
python scripts/convert_yolo_to_tflite.py \
  --model models/yolov8n.pt \
  --output models/yolov8n_fp32.tflite \
  --img-size 640
```

**Option B: On Your PC** (recommended)
```bash
# On your PC (Intel/Mac)
cd /path/to/pipeline-inspection

python scripts/convert_yolo_to_tflite.py \
  --model models/yolov8n.pt \
  --output models/yolov8n_fp32.tflite

# Transfer to ARM device
scp models/yolov8n_fp32.tflite user@arm-device:/path/to/pipeline-inspection/models/
```

## Step 4: Test Camera (30 sec)

```bash
# List cameras
v4l2-ctl --list-devices

# Test camera (should see your USB camera)
ls -la /dev/video*

# Quick camera test
python deployment/arm/test_tflite_inference.py --camera 0
```

Expected output:
```
✓ Camera opened: 640x480 @ 30fps
✓ Frame captured: (480, 640, 3)
```

## Step 5: Run Inference Test (1 min)

```bash
# Benchmark FP32 model on CPU
python deployment/arm/test_tflite_inference.py \
  --model models/yolov8n_fp32.tflite \
  --benchmark \
  --iterations 50
```

**Expected Results (ARM CPU only):**
```
📊 Benchmark Results:
   Average FPS:     5-8
   Average Latency: 120-200 ms
```

## Step 6: Live Inference (Optional)

```bash
# Run live inference with camera
python deployment/arm/test_tflite_inference.py \
  --model models/yolov8n_fp32.tflite \
  --camera 0 \
  --live

# Press 'q' to quit
```

## ✅ Success Checklist

- [ ] Camera detected and working
- [ ] TFLite model loaded successfully
- [ ] FPS: 5-8 (CPU-only, FP32)
- [ ] No errors in console

## 🚀 Next Steps

### Phase 1: FP32 Testing (You are here ✅)
You've validated:
- System runs on ARM
- Camera works
- TFLite inference works
- Baseline FPS established

### Phase 2: INT8 Quantization (Optional, +2x speed)
Even without NPU, INT8 on CPU is faster:

```bash
# Collect 100-300 real pipeline images
mkdir calibration_data
# ... add images ...

# Quantize to INT8
python scripts/convert_yolo_to_tflite.py \
  --model models/yolov8n.pt \
  --output models/yolov8n_int8.tflite \
  --quantize int8 \
  --calibration-data calibration_data

# Test INT8 model
python deployment/arm/test_tflite_inference.py \
  --model models/yolov8n_int8.tflite \
  --benchmark

# Expected: 10-15 FPS (2x faster than FP32)
```

### Phase 3: NPU Acceleration (Future, 30-60 FPS)
Requires:
- NPU delegate from chip vendor
- INT8 quantized model
- Additional configuration

See [`deployment/arm/README_ARM.md`](README_ARM.md#npu-acceleration-setup-production) for details.

## 🔧 Troubleshooting

### Camera Not Found
```bash
# Check USB connection
lsusb

# Check video devices
ls -la /dev/video*

# Try different index
python deployment/arm/test_tflite_inference.py --camera 1
```

### TFLite Import Error
```bash
# If tflite-runtime fails, use full TensorFlow
pip uninstall tflite-runtime
pip install tensorflow==2.15.0

# Update import in test script if needed
```

### Low Performance
This is **expected** on CPU-only FP32:
- FP32 on ARM CPU: 5-8 FPS ✓ (current)
- INT8 on ARM CPU: 10-15 FPS (next step)
- INT8 on ARM NPU: 30-60 FPS (production)

## 📊 Performance Roadmap

```
Current (FP32 CPU):     ████░░░░░░ 5-8 FPS
↓
INT8 CPU (easy):        ████████░░ 10-15 FPS
↓
INT8 NPU (production):  ██████████ 30-60 FPS
```

## 💡 Quick Commands Reference

```bash
# Test camera only
python deployment/arm/test_tflite_inference.py --camera 0

# Benchmark model
python deployment/arm/test_tflite_inference.py \
  --model models/yolov8n_fp32.tflite --benchmark

# Live inference
python deployment/arm/test_tflite_inference.py \
  --model models/yolov8n_fp32.tflite --live

# Convert YOLO to TFLite
python scripts/convert_yolo_to_tflite.py \
  --model models/yolov8n.pt \
  --output models/yolov8n_fp32.tflite
```

## ⏱️ Total Setup Time

- ✅ Environment setup: 5 min
- ✅ Model conversion: 2 min
- ✅ Testing: 3 min
- **Total: ~10 minutes**

## 📞 Support

Stuck? Check:
1. [`deployment/arm/README_ARM.md`](README_ARM.md) - Full ARM guide
2. Main [`README.md`](../../README.md) - General documentation
3. Test output logs for specific errors

---

**You're ready to deploy on ARM! 🎉**

Next: Train custom model on your pipeline defect data → INT8 quantization → NPU acceleration
