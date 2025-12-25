# Vercel Deployment Guide

## Overview

This project **cannot be fully deployed to Vercel** because it requires:
- USB camera access (physical hardware)
- Long-running WebSocket connections
- Real-time video processing

However, you can deploy the **frontend** to Vercel for demo purposes.

---

## Deployment Options

### Option 1: Frontend Demo on Vercel (UI Only)

Deploy the Next.js frontend to showcase the interface without backend.

#### Setup

1. **Create `vercel.json` configuration:**

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.com/api/:path*"
    },
    {
      "source": "/ws/:path*",
      "destination": "wss://your-backend-url.com/ws/:path*"
    }
  ]
}
```

2. **Deploy to Vercel:**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd /Users/wlin/dev/pipeline-inspection
vercel --prod
```

3. **Configure environment variables:**

In Vercel dashboard:
- `NEXT_PUBLIC_API_URL` = `https://your-backend-url.com`
- `NEXT_PUBLIC_WS_URL` = `wss://your-backend-url.com`

#### Update Frontend Code

Modify `frontend/components/VideoStream.tsx`:

```typescript
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

// In component
const ws = new WebSocket(`${WS_URL}/ws/video`);
```

Modify `frontend/app/page.tsx`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const response = await fetch(`${API_URL}/api/system/status`);
```

---

### Option 2: Hybrid Deployment (Recommended)

**Frontend:** Vercel (public, fast CDN)
**Backend:** Self-hosted (local/VPS with camera access)

#### Architecture

```
Internet Users
     ↓
Vercel (Frontend)
     ↓ HTTPS/WSS
Your Server (Backend + Camera)
```

#### Backend Hosting Options

| Option | Cost | Difficulty | Best For |
|--------|------|------------|----------|
| **Local PC/Mac** | Free | Easy | Demos, development |
| **VPS (DigitalOcean)** | $5-20/mo | Medium | Small deployment |
| **Dedicated Server** | $50+/mo | Medium | Production |
| **Raspberry Pi + Ngrok** | $10/mo | Easy | Home setup |

#### Example: Backend on Local + Ngrok

```bash
# 1. Install ngrok
brew install ngrok

# 2. Start backend locally
cd backend
source venv/bin/activate
python app.py

# 3. Expose via ngrok
ngrok http 8000

# 4. Copy ngrok URL (e.g., https://abc123.ngrok.io)

# 5. Update Vercel environment variables
NEXT_PUBLIC_API_URL=https://abc123.ngrok.io
NEXT_PUBLIC_WS_URL=wss://abc123.ngrok.io
```

---

### Option 3: Demo Mode (Static Mockup)

Deploy frontend with **mock data** for UI showcase.

#### Create Mock Data

```typescript
// frontend/lib/mockData.ts
export const mockDetections = [
  {
    class_name: "crack",
    confidence: 0.87,
    bbox: { x1: 120, y1: 200, x2: 340, y2: 280 },
    timestamp: new Date().toISOString(),
  },
  // ... more mock detections
];

export const mockVideo = "/demo-video.mp4"; // Add demo video to public/
```

#### Update Components

```typescript
// frontend/components/VideoStream.tsx
const useMockData = process.env.NEXT_PUBLIC_MOCK_MODE === 'true';

if (useMockData) {
  // Use mock data instead of WebSocket
  setInterval(() => {
    onNewDetection(mockDetections[Math.floor(Math.random() * mockDetections.length)]);
  }, 2000);
}
```

#### Deploy

```bash
# Set environment variable in Vercel
NEXT_PUBLIC_MOCK_MODE=true

# Deploy
vercel --prod
```

**Use case:** Portfolio, UI showcase, no backend needed

---

## Recommended Architecture (Production)

For actual production deployment with camera:

```
┌─────────────────────────────────────────────────┐
│  Edge Devices (ARM + NPU)                       │
│  ┌────────────────────────────────────────┐    │
│  │  Backend (FastAPI + Camera + YOLO)     │    │
│  └────────────────────────────────────────┘    │
│  Each device runs independently                 │
└──────────────────┬──────────────────────────────┘
                   │ Reports via API
                   ▼
         ┌─────────────────┐
         │  Cloud Dashboard │ ← Optional: Vercel
         │  (Aggregate View)│    Collect reports from devices
         └─────────────────┘
```

**Why not Vercel for backend?**
1. ❌ No USB device access
2. ❌ WebSocket connections timeout (10 sec limit on Hobby plan)
3. ❌ Not designed for real-time video streaming
4. ❌ Serverless functions are stateless (camera needs state)

---

## Alternative Cloud Platforms

If you need cloud deployment with camera access:

| Platform | WebSocket | Hardware | Cost | Best For |
|----------|-----------|----------|------|----------|
| **Vercel** | ❌ Limited | ❌ No | Free-$20 | Frontend only |
| **Railway** | ✅ Yes | ❌ No | $5-20 | Backend API |
| **Fly.io** | ✅ Yes | ❌ No | $0-10 | Full-stack apps |
| **AWS EC2** | ✅ Yes | ⚠️ With IoT | $10-50 | Enterprise |
| **DigitalOcean** | ✅ Yes | ❌ No | $5-20 | VPS hosting |
| **Self-hosted** | ✅ Yes | ✅ Yes | $0-50 | **Recommended** ⭐ |

---

## Deployment Checklist

### Frontend-Only Demo on Vercel

- [ ] Add environment variables for API/WS URLs
- [ ] Update API calls to use env vars
- [ ] Test CORS settings
- [ ] Deploy with `vercel --prod`
- [ ] Configure custom domain (optional)

### Hybrid (Frontend on Vercel + Backend Self-hosted)

- [ ] Deploy frontend to Vercel
- [ ] Set up backend on VPS/local
- [ ] Configure ngrok or public IP
- [ ] Update CORS to allow Vercel domain
- [ ] Set SSL certificates (for WSS)
- [ ] Test WebSocket connection

### Mock Demo Mode

- [ ] Create mock data
- [ ] Add demo video to `public/`
- [ ] Update components for mock mode
- [ ] Set `NEXT_PUBLIC_MOCK_MODE=true`
- [ ] Deploy to Vercel

---

## Vercel Deployment Commands

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy (interactive)
cd /Users/wlin/dev/pipeline-inspection
vercel

# Deploy to production
vercel --prod

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production

# View logs
vercel logs

# Remove deployment
vercel remove pipeline-inspection
```

---

## Recommended Setup for This Project

### Development
```
MacBook Pro (local)
├── Frontend: localhost:3000
└── Backend: localhost:8000 + USB camera
```

### Demo/Presentation
```
Frontend: Vercel (https://pipeline-inspection.vercel.app)
     ↓ WebSocket
Backend: ngrok (https://abc123.ngrok.io) + MacBook + camera
```

### Production
```
ARM Edge Devices (multiple units in field)
├── Frontend: Embedded web server (local network)
└── Backend: Local FastAPI + USB camera + NPU

Optional: Cloud dashboard (Vercel) for aggregate reporting
```

---

## Why Self-Hosting is Better for This Project

1. **Hardware Access** ✅
   - Direct USB camera access
   - No cloud latency
   - Offline operation

2. **Real-time Performance** ✅
   - No network delays
   - Instant WebSocket responses
   - Local processing (ARM+NPU)

3. **Cost Effective** ✅
   - One-time hardware cost
   - No monthly cloud fees
   - No bandwidth charges

4. **Data Privacy** ✅
   - Videos stay local
   - No cloud storage needed
   - GDPR/compliance friendly

5. **Reliability** ✅
   - Works without internet
   - No cloud service downtime
   - Predictable performance

---

## Summary

| Deployment Type | Feasibility | Use Case |
|----------------|-------------|----------|
| **Full system on Vercel** | ❌ Not possible | N/A |
| **Frontend only on Vercel** | ✅ Yes | UI demo, portfolio |
| **Hybrid (Vercel + Self-hosted)** | ✅ Yes | Demo with live data |
| **Self-hosted (Recommended)** | ✅ Yes | **Production** ⭐ |

**Conclusion:** Deploy frontend to Vercel for demos, but keep backend + camera self-hosted for production use.
