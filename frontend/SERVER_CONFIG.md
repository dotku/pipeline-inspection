# Frontend Server Configuration

The frontend now supports **flexible server configuration**, allowing you to connect to different backend servers.

## 🎯 Use Cases

1. **Development** → Connect to `localhost:8000`
2. **LAN Demo** → Connect to `192.168.1.100:8000`
3. **Remote Server** → Connect to `api.yourserver.com`
4. **Vercel Deployment** → Connect to backend wherever it's hosted

---

## 🔧 Configuration Methods

### Method 1: Environment Variables (Build-time)

**For deployment (Vercel, etc.):**

Create `frontend/.env.local`:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
NEXT_PUBLIC_WS_URL=ws://192.168.1.100:8000

# Or for production with SSL
NEXT_PUBLIC_API_URL=https://api.yourserver.com
NEXT_PUBLIC_WS_URL=wss://api.yourserver.com
```

**Restart the dev server:**
```bash
npm run dev
```

---

### Method 2: UI Configuration (Runtime) ⭐ Enabled by Default

**Users can change server without rebuilding:**

1. Click the **Settings icon** (⚙️) in the top-right corner
2. Enter the server URL:
   - **API URL**: `http://192.168.1.100:8000`
   - **WebSocket URL**: `ws://192.168.1.100:8000` (or click "Auto-generate")
3. Click **Save & Reload**

The configuration is saved in localStorage and persists across sessions.

**To reset to default:**
- Click Settings → Click **Reset**

---

## 📝 Configuration Examples

### Local Development
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### LAN Network (MacBook on same network)
```env
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
NEXT_PUBLIC_WS_URL=ws://192.168.1.100:8000
```

### Public Server with SSL
```env
NEXT_PUBLIC_API_URL=https://api.yourserver.com
NEXT_PUBLIC_WS_URL=wss://api.yourserver.com
```

### ngrok Tunnel
```env
NEXT_PUBLIC_API_URL=https://abc123.ngrok.io
NEXT_PUBLIC_WS_URL=wss://abc123.ngrok.io
```

---

## 🚀 Deployment Scenarios

### Scenario 1: Frontend on Vercel + Backend Local

**Frontend (Vercel):**
```env
# In Vercel dashboard → Environment Variables
NEXT_PUBLIC_API_URL=https://your-ngrok-url.ngrok.io
NEXT_PUBLIC_WS_URL=wss://your-ngrok-url.ngrok.io
```

**Backend (Local with ngrok):**
```bash
# Terminal 1: Start backend
cd backend
python app.py

# Terminal 2: Expose via ngrok
ngrok http 8000
```

Copy the ngrok URL and add to Vercel environment variables.

---

### Scenario 2: Frontend Deployed + Backend on VPS

**Frontend (Vercel/Netlify):**
```env
NEXT_PUBLIC_API_URL=https://vps.yourserver.com:8000
NEXT_PUBLIC_WS_URL=wss://vps.yourserver.com:8000
```

**Backend (VPS):**
```bash
# Ensure firewall allows port 8000
sudo ufw allow 8000

# Run backend with public access
cd backend
python app.py
```

---

### Scenario 3: All Local (Demo on MacBook)

**No configuration needed!** Default is `localhost:8000`.

Just run:
```bash
# Terminal 1: Backend
cd backend && python app.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

---

### Scenario 4: Frontend on Device A + Backend on Device B (Same LAN)

**Find backend device IP:**
```bash
# On Device B (backend)
ifconfig | grep "inet " | grep -v 127.0.0.1
# Example output: inet 192.168.1.100
```

**On Device A (frontend):**
- Open http://localhost:3000
- Click Settings (⚙️)
- Enter API URL: `http://192.168.1.100:8000`
- Click "Auto-generate" for WebSocket
- Save & Reload

---

## 🔒 CORS Configuration

Update `backend/app.py` to allow your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local dev
        "http://127.0.0.1:3000",           # Local dev
        "https://yourapp.vercel.app",      # Vercel
        "http://192.168.1.*",              # LAN (careful!)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 Testing Configuration

### Test API Connection

```bash
# From browser console or terminal
curl http://192.168.1.100:8000/api/system/status
```

Expected response:
```json
{
  "camera": {...},
  "detector": {...},
  "detections": {...}
}
```

### Test WebSocket Connection

Open browser console (F12) and run:
```javascript
const ws = new WebSocket('ws://192.168.1.100:8000/ws/video');
ws.onopen = () => console.log('WebSocket connected!');
ws.onerror = (e) => console.error('WebSocket error:', e);
```

---

## 🛠️ Troubleshooting

### "Failed to fetch" Error

**Cause:** API URL is wrong or backend is not running

**Fix:**
1. Verify backend is running: `curl http://localhost:8000`
2. Check API URL in Settings
3. Verify firewall allows the port

---

### WebSocket Connection Failed

**Cause:** WebSocket URL is wrong or blocked

**Fix:**
1. Use `ws://` for HTTP and `wss://` for HTTPS
2. Check browser console for errors
3. Verify CORS is configured correctly
4. Ensure backend supports WebSocket

---

### CORS Error

**Cause:** Backend doesn't allow frontend origin

**Fix:**
Add frontend URL to CORS whitelist in `backend/app.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "https://yourapp.vercel.app",  # Add this
],
```

---

### Settings Not Saving

**Cause:** LocalStorage is disabled or cleared

**Fix:**
- Enable localStorage in browser settings
- Check browser privacy settings
- Try incognito mode to test

---

## 📊 Configuration Priority

The system checks configuration in this order:

1. **Runtime Config** (localStorage) - Set via UI ⭐ Highest priority
2. **Environment Variables** (.env.local)
3. **Default** (localhost:8000) - Fallback

**Note:** Runtime configuration is enabled by default. To disable it, set:
```env
NEXT_PUBLIC_ALLOW_RUNTIME_CONFIG=false
```

---

## 🎯 Best Practices

### Development
✅ Use `localhost` (default)
✅ No configuration needed

### Demos (Same Location)
✅ Use `localhost` on MacBook
✅ Show UI to clients

### Demos (Remote)
✅ Frontend on Vercel
✅ Backend on MacBook with ngrok
✅ Configure via environment variables

### Production
✅ Frontend on edge device (embedded)
✅ Backend on same device (localhost)
✅ Or Frontend on Vercel + Backend on VPS

---

## 🚀 Quick Setup Examples

### Setup 1: Demo on MacBook
```bash
# No config needed!
cd /Users/wlin/dev/pipeline-inspection
./start_macos.sh
# Open http://localhost:3000
```

### Setup 2: Frontend on Vercel
```bash
# Deploy frontend
cd frontend
vercel --prod

# In Vercel dashboard, add env vars:
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_WS_URL=wss://your-backend-url.com
```

### Setup 3: LAN Demo
```bash
# On Backend Device (find IP first)
ifconfig | grep "inet "
# Note: 192.168.1.100

python backend/app.py

# On Frontend Device (browser)
# Open http://localhost:3000
# Click Settings → Enter 192.168.1.100:8000
```

---

## 📖 API Reference

### `getApiUrl(path)`
```typescript
import { getApiUrl } from '@/lib/config';

const url = getApiUrl('/api/system/status');
// Returns: http://localhost:8000/api/system/status
```

### `getWebSocketUrl(path)`
```typescript
import { getWebSocketUrl } from '@/lib/config';

const wsUrl = getWebSocketUrl('/ws/video');
// Returns: ws://localhost:8000/ws/video
```

### `setCustomServerUrl(apiUrl, wsUrl?)`
```typescript
import { setCustomServerUrl } from '@/lib/config';

setCustomServerUrl('http://192.168.1.100:8000');
// WebSocket URL auto-generated

// Or specify both:
setCustomServerUrl(
  'http://192.168.1.100:8000',
  'ws://192.168.1.100:8000'
);
```

### `clearCustomServerUrl()`
```typescript
import { clearCustomServerUrl } from '@/lib/config';

clearCustomServerUrl();
// Resets to default (localhost)
```

---

## ✅ Summary

**The frontend can now connect to any backend server:**
- ✅ localhost (default)
- ✅ LAN IP address
- ✅ Public domain/IP
- ✅ ngrok tunnel
- ✅ Any backend location

**Configuration is flexible:**
- Build-time (environment variables)
- Runtime (UI settings)
- No rebuild needed for runtime changes

**Perfect for:**
- Development
- Client demos
- Remote deployments
- Vercel hosting
- Production splits (Frontend CDN + Backend edge)
