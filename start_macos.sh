#!/bin/bash

# Pipeline Inspection System - macOS Quick Start
# Optimized for MacBook Pro demos and development

echo "🍎 Starting Pipeline Inspection System (macOS Demo Mode)"
echo ""

# Detect Apple Silicon
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    echo "✓ Detected Apple Silicon (M1/M2/M3)"
    PYTHON_CMD="python3"
else
    echo "✓ Detected Intel Mac"
    PYTHON_CMD="python3"
fi
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "⚠️  Homebrew not found!"
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Check if Python 3 is installed
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "⚠️  Python 3 not found!"
    echo "📦 Installing Python 3.11..."
    brew install python@3.11
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found!"
    echo "📦 Installing Node.js..."
    brew install node@20
fi

# Check if backend venv exists
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Backend virtual environment not found!"
    echo "📦 Creating virtual environment..."
    cd backend
    $PYTHON_CMD -m venv venv
    source venv/bin/activate

    echo "📦 Installing backend dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt

    # Apple Silicon specific packages
    if [ "$ARCH" = "arm64" ]; then
        echo "📦 Installing Apple Silicon optimizations..."
        pip install tensorflow-macos tensorflow-metal 2>/dev/null || echo "   ℹ️  TensorFlow Metal not available, using standard TensorFlow"
    fi

    cd ..
    echo "✅ Backend setup complete!"
    echo ""
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not found!"
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend setup complete!"
    echo ""
fi

# Check camera permissions on macOS
echo "📹 Checking camera permissions..."
echo "   If prompted, allow Terminal to access the camera"
echo "   Settings → Privacy & Security → Camera"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Pipeline Inspection System..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ System stopped"
    echo ""
    echo "📊 Demo Performance Summary:"
    echo "   Platform: macOS ($ARCH)"
    if [ "$ARCH" = "arm64" ]; then
        echo "   Expected FPS: 15-30 (Apple Silicon)"
    else
        echo "   Expected FPS: 8-18 (Intel)"
    fi
    echo ""
    echo "🚀 For production deployment (30-60 FPS):"
    echo "   See: deployment/arm/README_ARM.md"
    echo ""
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🐍 Starting Backend (FastAPI)..."
cd backend
source venv/bin/activate
$PYTHON_CMD app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "   Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "   ⚠️  Backend may have failed to start"
    echo "   Check logs above for errors"
fi

# Start frontend
echo "⚛️  Starting Frontend (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ System Started Successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PIPELINE INSPECTION SYSTEM - DEMO MODE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access Points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "💻 Platform: macOS $ARCH"
if [ "$ARCH" = "arm64" ]; then
    echo "🚀 Performance: 15-30 FPS (Apple Silicon - Great for demos!)"
else
    echo "🚀 Performance: 8-18 FPS (Intel - Good for demos)"
fi
echo ""
echo "📝 Demo Tips:"
echo "   1. Open http://localhost:3000 in browser"
echo "   2. Allow camera access if prompted"
echo "   3. Point camera at objects to test detection"
echo "   4. Generate sample report to show clients"
echo ""
echo "🎯 Production Deployment:"
echo "   ARM + NPU: 30-60 FPS at 5-8W power"
echo "   See: deployment/arm/README_ARM.md"
echo ""
echo "Press Ctrl+C to stop the system"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for processes
wait
