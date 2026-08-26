# Docker Setup Guide - IronOre CRM

Complete guide for building and running the IronOre CRM application using Docker.

## 📋 Prerequisites

- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)
- At least 4GB RAM available for containers
- Ports available: 80 (frontend), 8000 (backend), 1433 (database)

## 🚀 Quick Start

### 1. Prepare Environment Variables

```bash
# Copy the docker environment template
cp .env.docker .env
```

Edit `.env` and configure:
- `SA_PASSWORD` - SQL Server password (strong password recommended)
- `SECRET_KEY` - Generate a new secure key
- `SMTP_SERVER`, `SENDER_EMAIL`, `SENDER_PASSWORD` - Email configuration
- `OLLAMA_BASE_URL` - LLM service URL (optional)

### 2. Build and Start Services

```bash
# Build images and start all services
docker-compose up -d

# Or with verbose output
docker-compose up

# Watch logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. Access the Application

- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Database:** localhost:1433 (connect with SQL tools)

## 🔧 Docker Commands

### Build Services

```bash
# Build specific service
docker-compose build backend
docker-compose build frontend

# Build all services
docker-compose build

# Build without cache
docker-compose build --no-cache
```

### Manage Services

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart services
docker-compose restart

# Specific service restart
docker-compose restart backend
```

### View Logs and Status

```bash
# Real-time logs (all services)
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database

# Logs with timestamp
docker-compose logs -f -t
```

### Execute Commands in Containers

```bash
# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Run Python command in backend
docker-compose exec backend python -c "import sys; print(sys.version)"

# Check backend health
docker-compose exec backend curl http://localhost:8000/health
```

### Database Operations

```bash
# Access database shell
docker-compose exec database /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P <password>

# Database connection string
# Server: database
# Port: 1433
# User: SA
# Password: <SA_PASSWORD from .env>
```

## 📦 Image Information

### Backend Image
- **Base Image:** python:3.11-slim
- **Size:** ~150MB (optimized)
- **Includes:**
  - Python 3.11
  - FastAPI
  - Uvicorn
  - Required dependencies from requirements.txt
  - System dependencies (gcc, etc.)

### Frontend Image
- **Build Stage:** node:20-alpine
- **Production Stage:** nginx:alpine
- **Size:** ~30MB (optimized with multi-stage build)
- **Includes:**
  - Vite-built React application
  - Nginx web server
  - Proxy configuration for API calls

### Database Image
- **Base Image:** mssql/server:2019-latest
- **Size:** ~2GB+
- **Includes:**
  - SQL Server 2019 Express Edition
  - Full database features

## 🌐 Network Configuration

Services communicate via internal Docker network `crm-network`:

```
┌─────────────────────────────────────────────┐
│         Docker Network: crm-network         │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Frontend │  │ Backend  │  │ Database │ │
│  │  nginx   │→ │ FastAPI  │→ │ SQL Srv  │ │
│  │ :80      │  │ :8000    │  │ :1433    │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

### Service Communication

- **Frontend → Backend:** `http://backend:8000`
- **Backend → Database:** `mssql+pyodbc://SA:password@database:1433/ironore_crm`
- **External Access:**
  - Frontend: http://localhost:80
  - Backend: http://localhost:8000

## 🔐 Security Considerations

### Production Checklist

- [ ] Generate new `SECRET_KEY` (32+ characters)
- [ ] Use strong `SA_PASSWORD` (12+ chars, mixed case, numbers, symbols)
- [ ] Configure real SMTP credentials
- [ ] Update `VITE_API_BASE_URL` to production domain
- [ ] Enable HTTPS (use nginx reverse proxy/Traefik)
- [ ] Set appropriate log levels
- [ ] Review database backup strategy
- [ ] Configure resource limits in docker-compose
- [ ] Use secrets management (Docker Secrets, Vault, etc.)
- [ ] Regular security updates for base images

### Resource Limits (Optional)

Add to docker-compose.yml services:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🔄 Persistent Data

### Volumes

- **mssql-data:** Database files (persists across container restarts)
- **quotations:** Generated PDF quotations
- **app code:** Development volumes for live reload (can be removed in production)

### Backup Database

```bash
# Export database backup
docker-compose exec database /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U SA -P <password> \
  -Q "BACKUP DATABASE [ironore_crm] TO DISK='/var/opt/mssql/backup/ironore_crm.bak'"

# Copy backup to host
docker cp ironore-crm-database:/var/opt/mssql/backup/ironore_crm.bak ./backup/
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs <service_name>

# Verify configuration
docker-compose config

# Rebuild without cache
docker-compose build --no-cache <service_name>
```

### Port already in use

```bash
# Find process using port
# Windows
netstat -ano | findstr :80

# Linux/Mac
lsof -i :80

# Change port in docker-compose.yml
# Example: "8080:80" (external:internal)
```

### Database connection issues

```bash
# Test database connectivity
docker-compose exec backend python -c \
  "from sqlalchemy import create_engine; \
   engine = create_engine('mssql+pyodbc://SA:password@database:1433/ironore_crm?driver=ODBC+Driver+17+for+SQL+Server'); \
   connection = engine.connect(); print('Connected!')"
```

### API not responding

```bash
# Check backend health
docker-compose exec backend curl http://localhost:8000/health

# Check if service is running
docker-compose ps

# View backend logs
docker-compose logs backend
```

## 📝 Development Mode

For development with hot reload:

```bash
# Use docker-compose.override.yml or custom file
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# Frontend with live reload
docker-compose exec frontend npm run dev

# Backend with auto-reload
docker-compose up backend
```

## 🎯 Common Tasks

### Update Application Code

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

### Clear Everything and Start Fresh

```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove images
docker-compose down -v --rmi all

# Rebuild from scratch
docker-compose build --no-cache

# Start services
docker-compose up -d
```

### Scale Services

```bash
# Scale backend to 3 instances (requires load balancer configuration)
docker-compose up -d --scale backend=3
```

### Monitor Resources

```bash
# Watch container resource usage
docker stats

# Specific container
docker stats ironore-crm-backend

# Container details
docker inspect ironore-crm-backend
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)

## 🆘 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check Docker documentation
4. Verify environment variables in `.env`

---

**Last Updated:** August 26, 2026  
**Version:** 1.0
