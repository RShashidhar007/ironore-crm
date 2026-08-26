# 🐳 IronOre CRM - Docker Deployment Guide

Complete Docker setup for the IronOre CRM application with frontend, backend, and database.

## 🚀 Quick Start (2 minutes)

### Option 1: Automated (Recommended)

**Windows:**
```powershell
docker-start.bat
```

**Linux/Mac:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

### Option 2: Manual

```bash
# 1. Setup environment
cp .env.docker .env

# 2. Configure variables in .env (optional, defaults provided)

# 3. Start services
docker-compose up -d

# 4. Wait 10-15 seconds for services to initialize

# 5. Access application
# Frontend: http://localhost
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📋 What's Included

| Component | Details | Port |
|-----------|---------|------|
| **Frontend** | React + Vite → Nginx | 80 |
| **Backend** | FastAPI (Python 3.11) | 8000 |
| **Database** | SQL Server 2019 Express | 1433 |

## 📁 Files Created

```
.
├── docker-compose.yml           ← Service orchestration
├── .env.docker                  ← Environment template
├── DOCKER_SETUP.md              ← Full documentation
├── DOCKER_SUMMARY.md            ← Quick reference
├── docker-start.bat             ← Windows launcher
├── docker-start.sh              ← Linux/Mac launcher
├── backend/Dockerfile           ← Backend image
├── backend/.dockerignore        ← Backend build optimization
├── frontend/Dockerfile          ← Frontend image
└── frontend/.dockerignore       ← Frontend build optimization
```

## ⚙️ Configuration

### Default Environment (.env.docker)

```env
# Database
DATABASE_URL=mssql+pyodbc://SA:password@database:1433/ironore_crm
SA_PASSWORD=IronOre@2024!

# Backend
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# API
VITE_API_BASE_URL=http://localhost:8000

# Optional: LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=your-email@gmail.com
```

**⚠️ Before Production:**
- Generate new `SECRET_KEY`
- Use strong `SA_PASSWORD`
- Configure real SMTP credentials
- Update `VITE_API_BASE_URL` to production domain

## 🔌 Access Points

After starting services:

| Service | URL | Purpose |
|---------|-----|---------|
| Application | http://localhost | React frontend with chat |
| API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| Database | localhost:1433 | SQL Server connection |

## 🛠️ Common Commands

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop services (data persists)
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart services
docker-compose restart
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database
```

### Troubleshooting

```bash
# Check service status
docker-compose ps

# Execute command in container
docker-compose exec backend bash

# Check backend health
docker-compose exec backend curl http://localhost:8000/health

# Connect to database
docker-compose exec database sqlcmd -S localhost -U SA
```

## 📚 Documentation

- **DOCKER_SETUP.md** - Complete guide with advanced topics
- **DOCKER_SUMMARY.md** - Quick reference for all configurations

## ✅ Features

- ✓ Production-ready setup
- ✓ Health checks on all services
- ✓ Automatic restart policies
- ✓ Persistent data storage
- ✓ Internal service networking
- ✓ Comprehensive logging
- ✓ Security best practices
- ✓ Easy to scale and maintain

## 🔐 Security

### Checklist Before Production

- [ ] Generate new `SECRET_KEY` (32+ characters)
- [ ] Use strong `SA_PASSWORD`
- [ ] Configure real email credentials
- [ ] Update API URL to production domain
- [ ] Enable HTTPS (nginx reverse proxy)
- [ ] Use secrets management for sensitive data
- [ ] Regular database backups
- [ ] Monitor container resources
- [ ] Keep base images updated

## 🆘 Troubleshooting

### Ports Already in Use

```bash
# Check what's using port 80 (Windows)
netstat -ano | findstr :80

# Use different ports in docker-compose.yml
# Change: "80:80" to "8080:80"
```

### Database Connection Failed

```bash
# Check logs
docker-compose logs database

# Verify connection
docker-compose exec backend python -c \
  "from app.database import get_db; list(get_db())"
```

### Frontend Shows Blank Page

```bash
# Check frontend logs
docker-compose logs frontend

# Verify nginx is serving files
docker-compose exec frontend ls /usr/share/nginx/html/
```

## 📦 Sharing This Docker Setup

1. **Ensure .env.docker is in repository** (no secrets)
2. **Share the GitHub link** with team
3. **Provide quick start instructions:**
   ```bash
   git clone <repo>
   cd ironore-crm
   cp .env.docker .env
   docker-compose up -d
   ```

## 🎯 Next Steps

1. Run quick start script or `docker-compose up -d`
2. Wait 10-15 seconds for services to initialize
3. Open http://localhost in browser
4. Check backend at http://localhost:8000/docs
5. Check logs if issues: `docker-compose logs -f`

## 📞 Support

For issues:
1. Check `docker-compose logs -f`
2. Review DOCKER_SETUP.md
3. Verify .env configuration
4. Ensure ports are available
5. Check Docker is running and has enough resources

---

**Ready to Deploy! 🚀**

All components are production-ready. Follow the Quick Start section to get running in 2 minutes.
