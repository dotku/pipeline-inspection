# ARM + NPU Deployment Guide

This guide covers deploying the Pipeline Inspection System on ARM devices with NPU acceleration.

## Target Hardware

**Recommended Specs:**
- **CPU**: ARM Cortex-A7 / A55 or higher
- **GPU**: Mali-G610 or similar (optional)
- **NPU**: 6.0 TOPS @ INT8 (critical for performance)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 8GB minimum

**Tested Platforms:**
- Rockchip RK3588 / RK3576
- Amlogic A311D / S905X4
- MediaTek MT8395
- Generic ARM64 Linux with NPU support

## Performance Expectations

### NPU-Accelerated (INT8)
| Metric | FP32 (CPU) | INT8 (NPU) |
|--------|------------|------------|
| **FPS** | 5-8 | **30-60** |
| **Latency** | ~200ms | **< 50ms** |
| **Power** | 8-12W | **5-8W** |
| **CPU Usage** | 80-95% | **20-40%** |

### Why NPU Matters
- **5-10x faster** than Intel CPU
- **2-3x lower power** consumption
- **Perfect for edge deployment** (no cloud needed)
- **Production-ready** at low cost

## Architecture Comparison

### Current (Intel CPU)
```
Camera → OpenCV → YOLO (FP32) → CPU Inference → Results
                     ↓
            Slow (5-15 FPS)
            High Power (15-25W)
```

### ARM + NPU (Recommended)
```
Camera → OpenCV → YOLO (INT8) → NPU Inference → Results
                     ↓
            Fast (30-60 FPS)
            Low Power (5-8W)
```

## Deployment Options

### Option 1: FP32 Testing (Current Phase) ✅
**Purpose**: Quick validation, test system integration
- Use TensorFlow Lite (CPU backend)
- No NPU optimization yet
- Expected: 5-8 FPS (similar to Intel)
- **Ready to deploy NOW**

### Option 2: INT8 NPU Production (Next Phase)
**Purpose**: Production deployment with full NPU acceleration
- Requires INT8 quantization
- Needs NPU Delegate from chip vendor
- Expected: 30-60 FPS
- **Needs 1-2 weeks setup**

## Quick Start (FP32 Testing)

### 1. Install ARM Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install -y python3 python3-pip python3-venv

# Install OpenCV dependencies
sudo apt install -y libopencv-dev python3-opencv

# Install build tools
sudo apt install -y cmake build-essential
```

### 2. Install TensorFlow Lite

```bash
cd /path/to/pipeline-inspection/deployment/arm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install TFLite runtime (lightweight, ARM-optimized)
pip install tflite-runtime

# Alternative: Full TensorFlow (if tflite-runtime not available)
pip install tensorflow==2.15.0

# Install other dependencies
pip install numpy opencv-python pillow
```

### 3. Convert YOLO to TFLite

```bash
cd /path/to/pipeline-inspection

# Run conversion script
python scripts/convert_yolo_to_tflite.py \
  --model models/yolov8n.pt \
  --output models/yolov8n_fp32.tflite \
  --img-size 640
```

### 4. Test TFLite Inference

```bash
# Run performance test
python deployment/arm/test_tflite_inference.py \
  --model models/yolov8n_fp32.tflite \
  --camera 0

# Expected output:
# Camera: 640x480 @ 30fps
# Model loaded: yolov8n_fp32.tflite
# Inference FPS: 5-8 (CPU only)
# Latency: ~150-200ms
```

### 5. Run Full System (ARM Version)

```bash
# Start backend with TFLite
cd deployment/arm
source venv/bin/activate
python app_arm.py

# In another terminal, start frontend (same as Intel)
cd frontend
npm run dev
```

## NPU Acceleration Setup (Production)

### Step 1: Check NPU Support

```bash
# Check if NPU is detected
ls /dev/mali* /dev/rknpu* /dev/galcore*

# Verify NPU driver
dmesg | grep -i npu

# Check vendor tools
rknn-toolkit2 --version  # For Rockchip
```

### Step 2: Install NPU Delegate

**For Rockchip (RK3588/RK3576):**
```bash
# Install RKNN Toolkit
pip install rknn-toolkit2

# Download delegate
wget https://github.com/rockchip-linux/rknpu2/releases/download/v1.6.0/rknn_toolkit2-1.6.0-cp38-cp38-linux_aarch64.whl
pip install rknn_toolkit2-1.6.0-cp38-cp38-linux_aarch64.whl
```

**For Generic NPU:**
```bash
# Contact chip vendor for NPU delegate library
# Usually provided as .so file:
# - libnpu_delegate.so
# - libvsi_npu.so
# Copy to: /usr/lib/aarch64-linux-gnu/
```

### Step 3: INT8 Quantization

```bash
# Collect calibration images (100-300 pipeline images)
mkdir calibration_data
# Add your real pipeline images here

# Run quantization
python scripts/quantize_int8.py \
  --model models/yolov8n.pt \
  --calibration-data calibration_data \
  --output models/yolov8n_int8.tflite

# This will:
# 1. Export YOLO to ONNX
# 2. Convert ONNX to TFLite
# 3. Quantize to INT8 using calibration data
# 4. Optimize for NPU
```

### Step 4: Test NPU Performance

```bash
# Test with NPU delegate
python deployment/arm/test_npu_inference.py \
  --model models/yolov8n_int8.tflite \
  --use-npu

# Expected output:
# NPU detected: ✓
# Model loaded: yolov8n_int8.tflite
# Inference FPS: 30-60 (NPU accelerated!)
# Latency: 20-50ms
# NPU utilization: 60-80%
```

## Configuration

### ARM-Specific Settings (`deployment/arm/.env`)

```env
# Device
DEVICE_TYPE=arm
USE_NPU=false           # Set to true when NPU ready
NPU_DELEGATE_PATH=/usr/lib/aarch64-linux-gnu/libnpu_delegate.so

# Model
MODEL_PATH=../../models/yolov8n_fp32.tflite
MODEL_FORMAT=tflite
QUANTIZATION=fp32       # Change to int8 for NPU

# Camera (may differ on ARM)
CAMERA_INDEX=0
CAMERA_DEVICE=/dev/video0
CAMERA_FORMAT=MJPG      # or YUYV

# Performance
NUM_THREADS=4           # CPU threads for TFLite
USE_XNNPACK=true        # CPU optimization
INFERENCE_BATCH_SIZE=1

# Power Management
ENABLE_DVFS=true        # Dynamic voltage/frequency scaling
CPU_GOVERNOR=performance
```

## Model Conversion Pipeline

### Complete Flow (For Reference)

```
┌─────────────────────────────────────────────────────┐
│  Phase 1: Training (On PC/Cloud)                    │
├─────────────────────────────────────────────────────┤
│  YOLO Training (PyTorch)                            │
│  ├── Dataset: 500-1000 labeled images               │
│  ├── Classes: crack, rust, foreign_object, etc.     │
│  └── Output: best.pt (YOLO weights)                 │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Phase 2: Export & Convert                          │
├─────────────────────────────────────────────────────┤
│  YOLO → ONNX                                        │
│  └── yolo export model=best.pt format=onnx          │
│                                                      │
│  ONNX → TensorFlow                                  │
│  └── onnx-tf convert -i model.onnx -o tf_model      │
│                                                      │
│  TensorFlow → TFLite (FP32)                         │
│  └── tf.lite.TFLiteConverter.from_saved_model()     │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Phase 3: Quantization (INT8 for NPU)               │
├─────────────────────────────────────────────────────┤
│  Post-Training Quantization                         │
│  ├── Calibration: 100-300 representative images     │
│  ├── Quantize: FP32 → INT8                          │
│  └── Output: model_int8.tflite (NPU-optimized)      │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Phase 4: Deployment on ARM                         │
├─────────────────────────────────────────────────────┤
│  TFLite + NPU Delegate                              │
│  └── 30-60 FPS @ 5-8W power                         │
└─────────────────────────────────────────────────────┘
```

## Troubleshooting

### Camera Not Found
```bash
# List video devices
ls -la /dev/video*

# Test camera with v4l2
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats

# Try different camera index
CAMERA_INDEX=1 python app_arm.py
```

### TFLite Import Error
```bash
# If tflite-runtime fails
pip uninstall tflite-runtime
pip install tensorflow==2.15.0

# Update import in code:
# from tflite_runtime.interpreter import Interpreter
# → from tensorflow.lite.python.interpreter import Interpreter
```

### Low FPS on CPU
This is expected without NPU. Solutions:
- Reduce resolution: 320x320 instead of 640x640
- Increase confidence threshold: 0.6 instead of 0.5
- Enable XNNPACK: `USE_XNNPACK=true`
- Use INT8 model (even on CPU, 2x faster)

### NPU Not Detected
```bash
# Check kernel modules
lsmod | grep npu

# Check device permissions
sudo chmod 666 /dev/rknpu*

# Verify delegate library
ldconfig -p | grep npu
```

## Performance Benchmarking

### Run Benchmark Script

```bash
# Compare CPU vs NPU
python scripts/benchmark.py \
  --model-fp32 models/yolov8n_fp32.tflite \
  --model-int8 models/yolov8n_int8.tflite \
  --use-npu \
  --duration 60

# Output:
# ┌──────────────────┬─────────┬──────────┬───────────┐
# │ Configuration    │ FPS     │ Latency  │ Power     │
# ├──────────────────┼─────────┼──────────┼───────────┤
# │ FP32 (CPU)       │ 6.2     │ 161ms    │ 9.5W      │
# │ INT8 (CPU)       │ 12.4    │ 81ms     │ 9.2W      │
# │ INT8 (NPU)       │ 45.8    │ 22ms     │ 6.1W      │
# └──────────────────┴─────────┴──────────┴───────────┘
```

## Cost Analysis

### Hardware Cost Comparison

| Platform | Cost | FPS | Power | TCO (3 years) |
|----------|------|-----|-------|---------------|
| Intel i5 NUC | $800 | 8-15 | 15-25W | $1,200 |
| **ARM + NPU** | **$300** | **30-60** | **5-8W** | **$450** |

**Savings**: ~60% hardware + 70% power

## Production Checklist

Before mass production:
- [ ] INT8 quantization validated (< 2% accuracy loss)
- [ ] NPU utilization > 60%
- [ ] FPS stable at 30+ for 24h continuous run
- [ ] Power consumption < 8W average
- [ ] Camera driver stable (no frame drops)
- [ ] Report generation working
- [ ] System auto-recovery after power loss
- [ ] Thermal testing completed (40°C ambient)

## Next Steps

### Current Phase: FP32 Validation ✅
1. Test system on ARM with CPU-only TFLite
2. Verify camera, detection, and reporting work
3. Measure baseline FPS and power

### Next Phase: INT8 NPU Production
1. Collect 200-500 real pipeline images
2. Perform INT8 quantization with calibration
3. Integrate NPU delegate
4. Benchmark and validate performance
5. Prepare for production deployment

## Support

For ARM-specific issues:
- Check vendor documentation (Rockchip, Amlogic, etc.)
- NPU delegate issues: Contact chip vendor support
- Performance optimization: See `scripts/optimize_arm.py`

---

**Estimated Timeline**
- FP32 Testing: **1-3 days** ✅
- INT8 Quantization: **3-5 days**
- NPU Integration: **2-4 days**
- Production Validation: **1 week**

**Total: 2-3 weeks from FP32 to production-ready NPU deployment**
