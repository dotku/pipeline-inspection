#!/bin/bash

# Pipeline Inspection System - Quick Start Script

echo "🚀 Starting Pipeline Inspection System..."
echo ""

# Check if backend venv exists
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Backend virtual environment not found!"
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo "✅ Backend setup complete!"
    echo ""
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not found!"
    echo "📦 Installing dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend setup complete!"
    echo ""
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Pipeline Inspection System..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🐍 Starting Backend (FastAPI)..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting Frontend (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ System Started Successfully!"
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:3000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

# Wait for processes
wait
