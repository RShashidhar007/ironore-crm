# IronOre CRM - Docker Setup Guide

This guide explains how to build and run the IronOre CRM application in Docker.

## Files Created

- **`Dockerfile`** - Multi-stage build for frontend and backend
- **`.dockerignore`** - Files to exclude from Docker build
- **`docker-compose.yml`** - Orchestration for the application
- **`start.sh`** - Startup script to run backend and frontend
- **`.env.example`** - Environment variables template

## Prerequisites

- Docker Desktop (version 20.10+)
- Docker Compose (included with Docker Desktop)
- The existing `.env` file with your configuration (create from `.env.example` if needed)

## Quick Start

### 1. Build the Docker Image

```bash
cd d:\projects\ironore-crm
docker build -t ironore-crm:latest -f Dockerfile .
```

**What this does:**
- Stage 1: Builds the React/Vite frontend
- Stage 2: Prepares Python/FastAPI backend environment
- Stage 3: Combines both into single image with startup script

### 2. Run with Docker Compose

```bash
# Copy your environment file (if not already present)
cp .env.example .env
# Edit .env with your actual configuration

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### 3. Run Directly with Docker

```bash
docker run -d \
  --name ironore-crm \
  -p 8000:8000 \
  -p 5000:5000 \
  --env-file .env \
  ironore-crm:latest
```

### 4. Access the Application

- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Environment Configuration

Create a `.env` file in the project root with your configuration:

```bash
# Database
DB_MODE=mssql  # or sqlite for development
MSSQL_SERVER=your-server
MSSQL_DATABASE=Customer_DB
MSSQL_USER=your_user
MSSQL_PASSWORD=your_password

# Authentication
JWT_SECRET=your-secret-key

# Ollama (optional - for AI features)
OLLAMA_BASE_URL=http://ollama-host:11434
OLLAMA_MODEL=llama3.2

# Company Contact
COMPANY_SUPPORT_EMAIL=support@company.com
COMPANY_SUPPORT_PHONE=7022486778

# CORS
FRONTEND_ORIGIN=http://localhost:5000
```

## Database Configuration

### Option 1: SQL Server (Production)

```env
DB_MODE=mssql
MSSQL_SERVER=your-sql-server
MSSQL_PORT=1433
MSSQL_DATABASE=Customer_DB
MSSQL_USER=your_username
MSSQL_PASSWORD=your_password
MSSQL_ENCRYPT=no
MSSQL_TRUST_SERVER_CERT=yes
```

### Option 2: SQLite (Development)

```env
DB_MODE=sqlite
SQLITE_PATH=./customer_db.sqlite3
```

## Docker Compose Services

The `docker-compose.yml` defines:

- **Container**: `ironore-crm-app`
- **Ports**: 
  - `8000` - Backend (FastAPI)
  - `5000` - Frontend (static files)
- **Volumes**: `./data` - For SQLite database persistence
- **Network**: `crm-network` - Internal bridge network
- **Health Check**: Monitors `/api/health` endpoint

## Startup Script (start.sh)

The startup script:

1. Starts FastAPI backend on `0.0.0.0:8000`
2. Waits 2 seconds for backend to initialize
3. Starts Python HTTP server for frontend on `0.0.0.0:5000`
4. Displays connection information
5. Keeps both processes running

## Verifying the Setup

### Check Container Status

```bash
docker ps
docker-compose ps
```

### View Logs

```bash
docker logs ironore-crm-app
docker-compose logs -f crm-app
```

### Test Backend API

```bash
curl http://localhost:8000/api/health
```

### Test Frontend

```bash
curl http://localhost:5000
```

## Troubleshooting

### Container Won't Start

1. **Check logs**:
   ```bash
   docker-compose logs crm-app
   ```

2. **Common issues**:
   - Missing `.env` file → Create from `.env.example`
   - Database connection failed → Verify `MSSQL_*` variables
   - Port already in use → Check `docker ps` and stop conflicting containers

### Database Connection Error

```
Error: (pyodbc.OperationalError) ('08001', ...)
```

**Solution**: Verify `MSSQL_*` environment variables match your SQL Server:

```bash
# Test SQL Server connection from host
sqlcmd -S YOUR_SERVER -U YOUR_USER -P YOUR_PASSWORD
```

### Frontend Not Loading

- Verify frontend build: Check `frontend/dist/index.html` exists
- Rebuild if needed:
  ```bash
  cd frontend
  npm run build
  cd ..
  docker-compose up --build
  ```

### Ollama Connection Issues

If Ollama features fail:

```bash
# Option 1: Run Ollama locally
ollama serve

# Option 2: Disable Ollama in .env
OLLAMA_ENABLED=false

# Option 3: Point to remote Ollama
OLLAMA_BASE_URL=http://ollama-host:11434
```

## Development Workflow

### Local Development (Without Docker)

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Development with Docker (With Hot Reload)

```bash
# Build development image
docker-compose up --build

# Logs
docker-compose logs -f

# Rebuild if code changes
docker-compose down
docker-compose up --build
```

## Production Deployment

For production:

1. **Use environment-specific `.env` file**:
   ```bash
   export $(cat .env.prod | xargs)
   docker-compose -f docker-compose.yml up -d
   ```

2. **Set strong JWT_SECRET**:
   ```bash
   # Generate random secret
   openssl rand -hex 32
   ```

3. **Configure SQL Server** for production use

4. **Use reverse proxy** (nginx) for SSL/TLS

5. **Monitor logs**:
   ```bash
   docker-compose logs --tail=100 -f
   ```

## Cleaning Up

```bash
# Stop containers
docker-compose down

# Remove stopped containers
docker container prune

# Remove images
docker image rm ironore-crm:latest

# Remove volumes
docker volume prune
```

## Architecture

```
Docker Container
├── Backend (FastAPI on 0.0.0.0:8000)
│   ├── SQLAlchemy ORM
│   ├── ODBC (SQL Server connection)
│   └── Ollama integration
├── Frontend (Python HTTP on 0.0.0.0:5000)
│   └── React SPA (built with Vite)
└── Startup Script (start.sh)
    └── Runs both services simultaneously
```

## Networking

- **Inside Docker**: Services communicate via localhost
- **Outside Docker**: Access via localhost:8000 (backend) and localhost:5000 (frontend)
- **Database**: External SQL Server connection via environment variables

## Performance Notes

- **Build time**: ~2-3 minutes (includes downloading base images, dependencies)
- **Container size**: ~1.2-1.5 GB (node:20-alpine + python + dependencies)
- **Memory**: ~300-500 MB at rest
- **CPU**: Minimal unless running AI operations

## Next Steps

1. **Create `.env` file** from `.env.example`
2. **Configure database** connection settings
3. **Build image**: `docker build -t ironore-crm:latest .`
4. **Start container**: `docker-compose up -d`
5. **Access application**: http://localhost:5000

## Support

For issues:
- Check container logs: `docker-compose logs crm-app`
- Verify `.env` file configuration
- Ensure database is accessible from Docker container
- Check that all required ports (8000, 5000) are available
