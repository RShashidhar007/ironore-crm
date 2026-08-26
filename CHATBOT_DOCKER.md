# 🤖 IronOre CRM - Chatbot-Only Docker Setup

Minimal Docker deployment with just the floating chatbot button and backend API. Perfect for embedding in any website or using as a standalone chat service.

## 🚀 Quick Start (1 minute)

### Option 1: Automated

**Windows:**
```powershell
docker-start.bat
```

**Linux/Mac:**
```bash
./docker-start.sh
```

### Option 2: Manual

```bash
# 1. Setup environment
cp .env.docker .env

# 2. Start services (only backend + chatbot)
docker-compose up -d

# 3. Access chatbot
# Open http://localhost in your browser
```

## 📦 What's Included

| Component | Details | Port |
|-----------|---------|------|
| **Chatbot Frontend** | Standalone HTML with floating button | 80 |
| **Backend API** | FastAPI with chat endpoints | 8000 |

**Note:** Database is managed externally or you can use your own database connection string.

## 📁 Files

```
.
├── docker-compose.yml           ← 2 services only
├── .env.docker                  ← Configuration
├── frontend/
│   ├── Dockerfile              ← Nginx serving chatbot-only.html
│   └── chatbot-only.html       ← Standalone chatbot UI
└── backend/
    └── Dockerfile              ← FastAPI backend
```

## 🔌 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Chatbot** | http://localhost | Floating chat button |
| **Backend API** | http://localhost:8000 | Chat API endpoint |
| **API Docs** | http://localhost:8000/docs | API documentation |

## ⚙️ Configuration

### Minimal .env Setup

```env
# Database (use your existing database)
DATABASE_URL=mssql+pyodbc://SA:password@your-database:1433/ironore_crm

# Backend
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# API (frontend communicates with this)
VITE_API_BASE_URL=http://localhost:8000

# Optional: LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Optional: Email
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=your-email@gmail.com
```

## 🛠️ Common Commands

### Start/Stop

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Troubleshooting

```bash
# Check status
docker-compose ps

# Backend shell
docker-compose exec backend bash

# Check backend health
docker-compose exec backend curl http://localhost:8000/health
```

## 💾 Database Configuration

This setup doesn't include a database. You need to provide your own:

### Option 1: Connect to Existing Database
```
Update DATABASE_URL in .env to point to your existing SQL Server
```

### Option 2: Run Database Separately
```bash
# If you want to add database back, see DOCKER_SETUP.md
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword" \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2019-latest
```

### Option 3: Use Docker Compose with Database
```bash
# Uncomment database service in docker-compose.yml
# (See original docker-compose.yml for reference)
```

## 📱 Embedding the Chatbot

The chatbot is served as a standalone HTML file. You can:

1. **Access directly:** Open `http://localhost` in browser
2. **Embed in iframe:** 
   ```html
   <iframe src="http://your-domain:80" width="100%" height="100%"></iframe>
   ```
3. **Use as microservice:** Point your frontend to this chatbot service

## 🚢 Deployment Sizes

**Image Sizes (Approximate):**
- Backend: ~150MB (Python + FastAPI)
- Frontend: ~10MB (Nginx + HTML)
- **Total: ~160MB** (vs 2.3GB with full stack)

**Container Startup:**
- Full startup: ~5-10 seconds
- Very lightweight footprint

## 🔐 Security Notes

Before production:
- [ ] Generate new `SECRET_KEY`
- [ ] Use strong database password
- [ ] Configure real SMTP credentials
- [ ] Update API URL to production domain
- [ ] Enable HTTPS (nginx reverse proxy)
- [ ] Use secrets management

## 📊 Architecture

```
┌─────────────────────────────────┐
│      Docker Network              │
│      (crm-network)              │
├─────────────────────────────────┤
│                                 │
│  ┌──────────────┐  ┌──────────┐ │
│  │   Frontend   │  │ Backend  │ │
│  │   (Nginx)    │→ │(FastAPI) │ │
│  │   Port 80    │  │Port 8000 │ │
│  └──────────────┘  └──────────┘ │
│                        ↓         │
│                   Your Database  │
│                 (external/custom)│
└─────────────────────────────────┘
```

## 🔄 Workflow

1. User opens chatbot in browser
2. Clicks floating button (bottom-right)
3. Types message → Sends to Backend API
4. Backend processes → Returns response
5. Frontend updates chat with reply

## 🌐 Use Cases

✓ **Embed in existing website** - Use iframe or direct link
✓ **Standalone service** - Share URL with team
✓ **Mobile app chatbot** - Backend-only, custom UI
✓ **Multi-tenant deployment** - Scale backend, replicate frontend
✓ **Lightweight microservice** - Minimal resource usage

## 📚 Full Documentation

For complete setup with database and all features, see:
- **DOCKER_SETUP.md** - Full 3-service setup
- **DOCKER_README.md** - Complete guide

## 🆘 Troubleshooting

### Chatbot shows blank page
```bash
docker-compose logs frontend
```

### Backend not responding
```bash
docker-compose logs backend
# Check DATABASE_URL in .env
```

### Port 80 already in use
```bash
# Change port in docker-compose.yml
# "8080:80" instead of "80:80"
```

### Can't connect to database
```bash
# Verify DATABASE_URL in .env
# Check database is running and accessible
docker-compose logs backend
```

## 🎯 Next Steps

1. Configure `.env` with your database
2. Run `docker-compose up -d`
3. Open `http://localhost`
4. Test chatbot functionality
5. Deploy/share URL with team

---

**Ready to go! Minimal, lightweight, production-ready.** 🚀
