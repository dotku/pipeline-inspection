# Camera Configuration Guide

The Pipeline Inspection System supports both **USB cameras** and **RTSP streams** as video sources.

## 🎥 Camera Source Types

### 1. USB Camera (Default)
- Local camera connected directly to the device
- Typically webcams or industrial USB camera modules
- Identified by index number (0, 1, 2, etc.)

### 2. RTSP Stream
- Network cameras (IP cameras)
- Video streaming servers
- Remote video sources
- Any RTSP-compatible source

---

## 🔧 Configuration Methods

### Method 1: Frontend UI (Recommended)

**Steps:**
1. Click the **Camera icon** (🎥) in the top-right corner
2. Select source type:
   - **USB Camera** - for local cameras
   - **RTSP Stream** - for network streams
3. Enter configuration:
   - **USB**: Camera index (usually 0, 1, 2, etc.)
   - **RTSP**: Full RTSP URL
4. Click **Apply & Restart Camera**

The camera will automatically restart with the new source.

---

### Method 2: API Endpoint

**Set Camera Source:**
```bash
# USB Camera (index 0)
curl -X POST http://localhost:8000/api/camera/source \
  -H "Content-Type: application/json" \
  -d '{"source": "0"}'

# RTSP Stream
curl -X POST http://localhost:8000/api/camera/source \
  -H "Content-Type: application/json" \
  -d '{"source": "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"}'
```

**Get Current Source:**
```bash
curl http://localhost:8000/api/camera/source
```

**Response:**
```json
{
  "source": "rtsp://example.com/stream",
  "type": "RTSP",
  "is_opened": true
}
```

---

## 📝 RTSP URL Examples

### Public Test Streams

**Big Buck Bunny (Wowza Demo):**
```
rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov
```

**RTSP Test Server:**
```
rtsp://rtsp.stream/pattern
```

### IP Camera Examples

**Generic IP Camera:**
```
rtsp://username:password@192.168.1.100:554/stream1
```

**Hikvision Camera:**
```
rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101
```

**Dahua Camera:**
```
rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0
```

**Axis Camera:**
```
rtsp://username:password@192.168.1.100/axis-media/media.amp
```

**Amcrest Camera:**
```
rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=1
```

---

## 🖥️ Backend Configuration

### Environment Variables

Add to `backend/.env`:

```env
# Default camera source
CAMERA_INDEX=0  # For USB camera
# Or use RTSP URL directly (requires code modification)
```

### Python Code

```python
from camera import Camera

# USB Camera
camera = Camera(camera_source=0)

# RTSP Stream
camera = Camera(camera_source="rtsp://example.com/stream")

camera.open()
ret, frame = camera.read_frame()
camera.close()
```

---

## 🔍 Troubleshooting

### RTSP Connection Failed

**Symptoms:**
- Camera fails to open
- "Failed to open RTSP stream" error
- No video feed in frontend

**Solutions:**

1. **Test the RTSP URL with VLC:**
   ```bash
   vlc rtsp://your-camera-url
   ```
   If VLC can't open it, the URL is incorrect.

2. **Check network connectivity:**
   ```bash
   ping 192.168.1.100  # IP camera address
   ```

3. **Verify RTSP port is open:**
   ```bash
   telnet 192.168.1.100 554
   ```

4. **Check credentials:**
   - Ensure username and password are correct
   - URL format: `rtsp://username:password@ip:port/path`

5. **Firewall issues:**
   - RTSP typically uses port 554
   - May also need ports 8554, 8555 for some cameras

---

### USB Camera Not Detected

**Symptoms:**
- Camera index returns "Failed to open camera"
- Available cameras list is empty

**Solutions:**

1. **List available cameras:**
   ```bash
   curl http://localhost:8000/api/cameras/list
   ```

2. **Check camera permissions:**
   ```bash
   # macOS
   sudo killall VDCAssistant

   # Linux
   ls -l /dev/video*
   sudo chmod 666 /dev/video0
   ```

3. **Try different camera indices:**
   - Built-in camera: usually index 0
   - External USB camera: usually index 1, 2, etc.

---

### Low Frame Rate with RTSP

**Symptoms:**
- Streaming is slow
- High latency
- Choppy video

**Solutions:**

1. **Network bandwidth:**
   - Ensure good network connection
   - Use wired connection instead of WiFi
   - Check for network congestion

2. **Camera settings:**
   - Lower the camera's resolution
   - Reduce bitrate in camera settings
   - Use H.264 instead of MJPEG

3. **Backend optimization:**
   - The system uses the stream's native FPS
   - Resolution/FPS cannot be changed for RTSP streams (camera-controlled)

---

### RTSP Stream Works but Detection Fails

**Symptoms:**
- Video feed displays
- No detections appearing
- YOLO model not running

**Solutions:**

1. **Check model is loaded:**
   ```bash
   curl http://localhost:8000/api/system/status
   ```
   Verify `detector.is_loaded: true`

2. **Verify frame format:**
   - RTSP frames are automatically converted by OpenCV
   - Should work with any standard RTSP stream

3. **Check confidence threshold:**
   - Default is 0.5 (50%)
   - May need to lower for different content
   - Modify in `backend/config.py`

---

## 🎯 Use Cases

### Use Case 1: Local Pipeline Inspection (USB Camera)

```
Configuration:
- Source Type: USB Camera
- Camera Index: 0

Best for:
- Field inspections
- Portable setups
- MacBook demos
- ARM edge devices
```

### Use Case 2: Fixed Installation (IP Camera)

```
Configuration:
- Source Type: RTSP Stream
- URL: rtsp://admin:password@192.168.1.100:554/stream1

Best for:
- Permanent installations
- Remote monitoring
- Multiple camera setups
- Centralized inspection systems
```

### Use Case 3: Video File Analysis (RTSP Server)

```
Configuration:
- Source Type: RTSP Stream
- URL: rtsp://localhost:8554/video-file

Setup:
1. Use MediaMTX or FFmpeg to serve video file as RTSP
2. Point system to RTSP URL
3. Process archived pipeline videos

Best for:
- Testing with recorded footage
- Batch processing historical data
- Demo with consistent content
```

---

## 🚀 Advanced Setup

### Serve Video File as RTSP (FFmpeg)

**Stream a video file:**
```bash
ffmpeg -re -i pipeline_video.mp4 \
  -c copy \
  -f rtsp \
  rtsp://localhost:8554/stream
```

**Stream with transcoding:**
```bash
ffmpeg -re -i pipeline_video.mp4 \
  -vcodec libx264 \
  -preset ultrafast \
  -f rtsp \
  rtsp://localhost:8554/stream
```

### Multiple Camera Support (Future Enhancement)

Currently, the system supports one camera at a time. For multiple cameras:

1. Run multiple backend instances on different ports
2. Each instance connects to a different camera
3. Frontend can switch between backend servers

---

## 📊 Performance Comparison

| Camera Type | Latency | FPS | Resolution | Use Case |
|------------|---------|-----|------------|----------|
| USB Camera | <50ms | 15-30 | Configurable | Local inspection |
| RTSP (LAN) | 100-300ms | 15-25 | Fixed | Network camera |
| RTSP (WAN) | 500ms-2s | 10-20 | Fixed | Remote monitoring |

---

## ✅ Quick Reference

**Switch to USB Camera:**
```bash
curl -X POST http://localhost:8000/api/camera/source \
  -H "Content-Type: application/json" \
  -d '{"source": "0"}'
```

**Switch to RTSP Stream:**
```bash
curl -X POST http://localhost:8000/api/camera/source \
  -H "Content-Type: application/json" \
  -d '{"source": "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"}'
```

**Check Current Source:**
```bash
curl http://localhost:8000/api/camera/source
```

**System Status:**
```bash
curl http://localhost:8000/api/system/status
```

---

## 📖 API Reference

### POST /api/camera/source
Set camera source (USB or RTSP)

**Request:**
```json
{
  "source": "0"  // or "rtsp://..."
}
```

**Response:**
```json
{
  "message": "Camera source set to USB camera 0",
  "source": 0,
  "type": "USB",
  "status": "opened"
}
```

### GET /api/camera/source
Get current camera source

**Response:**
```json
{
  "source": "rtsp://example.com/stream",
  "type": "RTSP",
  "is_opened": true
}
```

### GET /api/cameras/list
List available USB cameras

**Response:**
```json
{
  "available_cameras": [0, 1],
  "current_source": 0,
  "current_type": "USB"
}
```

---

## 🎉 Summary

The Pipeline Inspection System now supports:

✅ **USB Cameras** - Local camera devices
✅ **RTSP Streams** - Network IP cameras
✅ **Runtime Switching** - Change source without restart
✅ **Frontend UI** - Easy configuration interface
✅ **API Control** - Programmatic camera management

**Perfect for:**
- Local inspections with USB cameras
- Remote monitoring with IP cameras
- Testing with RTSP test streams
- Flexible deployment scenarios
