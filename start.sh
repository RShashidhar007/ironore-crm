#!/bin/sh
# ============================================================
# Startup script for IronOre CRM Docker container
# Starts both Backend (FastAPI) and Frontend (static server)
# ============================================================

set -e

echo "=========================================="
echo "IronOre CRM - Docker Container Startup"
echo "=========================================="

# Start backend FastAPI server on 0.0.0.0:8000
echo "[1/2] Starting FastAPI Backend Server..."
cd /app/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 2

# Start frontend static server on 0.0.0.0:5000
echo "[2/2] Starting Frontend Server..."
cd /app/frontend/dist
python3 -m http.server 5000 --bind 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "Application Started Successfully!"
echo "=========================================="
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5000"
echo "API Docs: http://localhost:8000/docs"
echo "=========================================="

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
