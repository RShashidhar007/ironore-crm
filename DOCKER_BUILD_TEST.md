# Docker Build & Test Commands

## Build the Docker Image

```bash
cd d:\projects\ironore-crm

# Build the image
docker build -t ironore-crm:latest -f Dockerfile .

# Or with verbose output
docker build -t ironore-crm:latest -f Dockerfile . --progress=plain
```

**Build Output Should Include:**
```
✓ STAGE 1: Frontend build complete
✓ STAGE 2: Python dependencies installed
✓ STAGE 3: Combined image created
Successfully tagged ironore-crm:latest
```

## Run the Container

### Option 1: Using docker-compose (Recommended)

```bash
cd d:\projects\ironore-crm

# Create .env file from template
cp .env.example .env

# Edit .env with your configuration:
# - MSSQL_SERVER=your-server
# - MSSQL_USER=your-user
# - MSSQL_PASSWORD=your-password
# - JWT_SECRET=your-secret

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f crm-app

# Stop the application
docker-compose down
```

### Option 2: Using docker run directly

```bash
cd d:\projects\ironore-crm

# Run the container
docker run -d \
  --name ironore-crm-app \
  -p 8000:8000 \
  -p 5000:5000 \
  --env-file .env \
  ironore-crm:latest

# View logs
docker logs -f ironore-crm-app

# Stop the container
docker stop ironore-crm-app

# Remove the container
docker rm ironore-crm-app
```

## Verify the Application is Running

### 1. Check Container Status

```bash
# Check if container is running
docker ps

# Should show: ironore-crm-app with ports 8000 and 5000 exposed
```

### 2. Check Backend Health

```bash
# Option 1: Using curl
curl http://localhost:8000/api/health

# Option 2: Using PowerShell
Invoke-WebRequest http://localhost:8000/api/health

# Expected response: 200 OK with health status
```

### 3. Check Frontend Access

```bash
# Option 1: Using curl
curl http://localhost:5000

# Option 2: Using PowerShell
Invoke-WebRequest http://localhost:5000

# Expected: HTML content of the React application
```

### 4. View Application Logs

```bash
# Backend logs
docker-compose logs crm-app

# Live logs (follow mode)
docker-compose logs -f crm-app

# Last 50 lines
docker-compose logs --tail=50 crm-app
```

## Test URLs

Open these in your browser:

| URL | Purpose | Expected |
|-----|---------|----------|
| http://localhost:5000 | Frontend | React CRM Interface |
| http://localhost:8000 | Backend root | API documentation |
| http://localhost:8000/docs | API Swagger UI | Interactive API explorer |
| http://localhost:8000/api/health | Health check | `{"status": "ok"}` |

## Database Connection Testing

### Test SQL Server Connection from Container

```bash
# Access container shell
docker exec -it ironore-crm-app sh

# Inside container, test database
python3 -c "
from app.config import settings
print('DB Mode:', settings.DB_MODE)
print('Database URI configured')
"
```

## Troubleshooting Build Failures

### Build Error: "Frontend build failed"

```bash
# Rebuild with verbose output
docker build -t ironore-crm:latest -f Dockerfile . --progress=plain

# Check that frontend/dist exists locally
ls frontend/dist/index.html

# If missing, build frontend first
cd frontend
npm run build
cd ..
```

### Build Error: "Python dependencies failed"

```bash
# Check requirements.txt
cat backend/requirements.txt

# Verify image has Python
docker run --rm python:3.11-slim python --version
```

### Build Error: "ODBC Driver not found"

This is expected - ODBC is for SQL Server connection. The container includes system support but actual connection happens at runtime with environment variables.

## Troubleshooting Runtime Issues

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs crm-app

# Common errors:
# 1. "Port already in use" -> docker ps, docker stop container
# 2. ".env file not found" -> cp .env.example .env
# 3. "Database connection failed" -> verify MSSQL_ variables in .env
```

### API Returns 500 Error

```bash
# Check backend logs
docker-compose logs crm-app | grep ERROR

# Test database connection from container
docker exec ironore-crm-app python3 -c "
from sqlalchemy import create_engine
from app.config import settings
engine = create_engine(settings.sqlalchemy_database_uri)
connection = engine.connect()
print('Database connection successful!')
"
```

### Frontend Shows "Cannot Connect to Backend"

```bash
# Check backend is running
docker exec ironore-crm-app curl http://localhost:8000/api/health

# Check FRONTEND_ORIGIN matches your setup
echo "FRONTEND_ORIGIN=$(cat .env | grep FRONTEND_ORIGIN)"

# Verify ports are mapped
docker port ironore-crm-app
```

## Performance Testing

### Check Container Resource Usage

```bash
# Real-time resource monitor
docker stats ironore-crm-app

# Memory usage
docker exec ironore-crm-app ps aux

# Disk size
docker image ls ironore-crm
```

### Test API Response Time

```bash
# Using curl with timing
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# Or PowerShell
$response = Measure-Command { Invoke-WebRequest http://localhost:8000/api/health }
$response.TotalMilliseconds
```

## Cleanup Commands

```bash
# Stop and remove containers
docker-compose down

# Remove the image
docker image rm ironore-crm:latest

# Remove unused images/volumes
docker image prune -a
docker volume prune

# Full cleanup
docker system prune -a
```

## Debugging Commands

### Access Container Shell

```bash
docker exec -it ironore-crm-app sh
```

### Check Installed Packages

```bash
# Python packages
docker exec ironore-crm-app pip list

# Node modules
docker exec ironore-crm-app ls -la node_modules
```

### Inspect Container Configuration

```bash
# View environment variables
docker exec ironore-crm-app env

# View startup process
docker exec ironore-crm-app ps aux

# View open ports
docker exec ironore-crm-app netstat -tlnp
```

## Success Indicators

✅ Build succeeds without errors
✅ Container starts with 0.0.0.0 binding
✅ Logs show both backend and frontend starting
✅ Frontend accessible at http://localhost:5000
✅ Backend API accessible at http://localhost:8000
✅ Health check returns 200 OK
✅ Frontend can communicate with backend
✅ Database connection succeeds (if configured)

## Next Steps After Successful Test

1. ✅ Verify build is reproducible
2. ✅ Test with different `.env` configurations
3. ✅ Verify database persistence (if using volumes)
4. ✅ Test with production environment
5. ✅ Set up health monitoring
6. ✅ Configure reverse proxy (nginx) if deploying
