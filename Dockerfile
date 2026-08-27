# ============================================================
# Multi-stage Dockerfile for IronOre CRM
# ============================================================
# Stage 1: Build the frontend (React/Vite)
# Stage 2: Build the backend runtime (Python/FastAPI)
# ============================================================

# ============================================================
# STAGE 1: Frontend Build
# ============================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html ./
COPY frontend/vite.config.js ./

# Build frontend
RUN npm run build

# ============================================================
# STAGE 2: Backend Runtime
# ============================================================
FROM python:3.11-slim

# Install system dependencies for ODBC (SQL Server connection)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Copy Python requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/app ./app
COPY backend/.env.example .env.example

# ============================================================
# STAGE 3: Frontend Server + Backend Server Combined
# ============================================================
FROM node:20-alpine

# Install Python in the final image to run FastAPI
RUN apk add --no-cache python3 py3-pip python3-dev gcc musl-dev linux-headers curl

WORKDIR /app

# Copy Python from stage 2
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin/python* /usr/local/bin/

# Copy frontend build from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy backend code
COPY backend/app ./backend/app
COPY backend/requirements.txt ./backend/

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose ports
# 8000 = Backend (FastAPI)
# 5000 = Frontend (nginx/simple server)
EXPOSE 8000 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start both backend and frontend
CMD ["./start.sh"]
