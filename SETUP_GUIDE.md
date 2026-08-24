# Iron Ore CRM - Complete Setup Guide

This guide provides step-by-step instructions for setting up the entire Iron Ore CRM system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** & npm - [Download](https://nodejs.org/)
- **SQL Server 2019+** - [Download](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
- **Ollama** - [Download](https://ollama.ai)
- **Git** - [Download](https://git-scm.com)

### System Requirements

- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for Ollama model download
- **OS**: Windows 10+, macOS 10.14+, or Ubuntu 18+

### Verify Installation

```bash
# Check Python
python --version

# Check Node.js
node --version
npm --version

# Check Git
git --version
```

---

## Database Setup

### 1. Create SQL Server Database

```sql
-- Using SQL Server Management Studio or sqlcmd

-- Create database
CREATE DATABASE Customer_DB;

-- Use the database
USE Customer_DB;

-- Create login if not exists
IF NOT EXISTS (SELECT * FROM sys.sql_logins WHERE name = 'crm_user')
    CREATE LOGIN crm_user WITH PASSWORD = 'Shashi@2005';

-- Create user
CREATE USER crm_user FOR LOGIN crm_user;

-- Grant permissions
ALTER ROLE db_owner ADD MEMBER crm_user;
```

### 2. Run Migration Scripts

```bash
# From backend directory
cd backend

# Run migrations
python scripts/migrate_database.py
```

### 3. Populate Sample Data

```bash
# Populate products and inventory
python scripts/populate_inventory_data.py

# Add test complaints (optional)
python scripts/populate_complaint.py
```

### 4. Verify Database

```bash
# Check schema
python scripts/check_inventory_schema.py
```

---

## Backend Setup

### 1. Clone Repository

```bash
git clone https://github.com/RShashidhar007/ironore-crm.git
cd ironore-crm/backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env with your settings
```

**Important .env Variables:**

```env
# Database Configuration
MSSQL_SERVER=SHASHIDHAR\SQLEXPRESS
MSSQL_DATABASE=Customer_DB
MSSQL_USER=crm_user
MSSQL_PASSWORD=Shashi@2005

# AI Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_ENABLED=true

# Company Settings
COMPANY_SUPPORT_EMAIL=rshashidhar513@gmail.com
COMPANY_SUPPORT_PHONE=7022486778

# JWT
JWT_SECRET=your-random-secret-key-change-this-in-production
JWT_EXPIRE_MINUTES=120

# Frontend
FRONTEND_ORIGIN=http://localhost:5173
```

### 5. Start Backend Server

```bash
python -m uvicorn app.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 6. Verify Backend

Open browser and go to: `http://localhost:8000/docs`

You should see the interactive API documentation.

---

## Frontend Setup

### 1. Navigate to Frontend

```bash
cd ../frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env
```

**Frontend .env:**

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 4. Start Development Server

```bash
npm run dev
```

**Expected Output:**
```
  VITE v5.4.21  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

---

## Running the Application

### Start All Services (In Order)

**Terminal 1 - SQL Server**
```bash
# Ensure SQL Server is running
# (Usually starts automatically on Windows)
```

**Terminal 2 - Ollama**
```bash
ollama serve
```

Wait for message: `Listening on 127.0.0.1:11434`

**Terminal 3 - Backend**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload
```

Wait for: `Application startup complete`

**Terminal 4 - Frontend**
```bash
cd frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Test Login

Use these credentials to test:
- **Username**: shashi
- **Password**: test123

---

## Testing

### 1. Test Backend

```bash
# Test quotation feature
cd backend
python tests/test_quotation_flow.py

# Test email feature
python tests/test_email_feature.py
```

### 2. Test Frontend (Manual)

1. Open http://localhost:5173
2. Login with test credentials
3. Test each feature:
   - Ask for a Quotation
   - Place an Order
   - Raise a Complaint
   - Track Complaint
   - Contact Company

### 3. Test API Directly

```bash
# Using curl
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id":"shashi","password":"test123"}'
```

---

## Troubleshooting

### SQL Server Connection Issues

**Error**: "Could not connect to instance 'SQLEXPRESS'"

```bash
# Check if SQL Server is running
# Windows: Services app → SQL Server (SQLEXPRESS)

# Or verify connection:
sqlcmd -S SHASHIDHAR\SQLEXPRESS -U crm_user -P "Shashi@2005"
```

### Ollama Connection Issues

**Error**: "Failed to connect to Ollama"

```bash
# 1. Verify Ollama is running
# Visit: http://localhost:11434/

# 2. Pull the model
ollama pull llama3.2

# 3. Check OLLAMA_BASE_URL in .env
# Should be: http://localhost:11434
```

### Port Already in Use

**Error**: "Address already in use"

```bash
# Find process on port
# Windows: netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

### Module Not Found

**Error**: "ModuleNotFoundError: No module named 'fastapi'"

```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Connection String Issues

**Verify connection string format:**

```python
# Format: Server=hostname\instance_name;Database=db_name;User Id=user;Password=pass

# Examples:
MSSQL_SERVER=localhost\SQLEXPRESS
MSSQL_SERVER=COMPUTER_NAME\SQLEXPRESS
MSSQL_SERVER=192.168.1.100\SQLEXPRESS
```

### Npm Install Issues

**Error**: "npm ERR! code ERESOLVE"

```bash
# Clear npm cache
npm cache clean --force

# Install with legacy dependency resolution
npm install --legacy-peer-deps
```

---

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit files in `backend/app/`
   - Server auto-reloads (with `--reload` flag)
   - Test with `python tests/` scripts

2. **Frontend Changes**:
   - Edit files in `frontend/src/`
   - Dev server hot-reloads automatically
   - Test in browser

3. **Database Changes**:
   - Create migration script in `backend/database/`
   - Run migration
   - Verify with schema check

### Pushing to GitHub

```bash
# Stage changes
git add .

# Create meaningful commit
git commit -m "feat: add new feature description"

# Push to repository
git push origin main

# Or push to feature branch
git push origin feature/feature-name
```

---

## Deployment

### Production Build

```bash
# Frontend
cd frontend
npm run build
# Creates optimized build in dist/

# Backend
# No build needed, use with gunicorn in production
```

### Environment Variables for Production

```bash
# Backend
JWT_SECRET=<generate-random-secret>
OLLAMA_ENABLED=false  # Disable if using API only
FRONTEND_ORIGIN=https://yourdomain.com

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## Quick Reference

### Important Directories

| Directory | Purpose |
|-----------|---------|
| `backend/app/` | Main application code |
| `backend/database/` | SQL migration scripts |
| `backend/scripts/` | Utility scripts |
| `backend/tests/` | Test scripts |
| `frontend/src/` | React components and pages |
| `frontend/public/` | Static assets |

### Common Commands

```bash
# Backend
pip install -r requirements.txt        # Install dependencies
python scripts/migrate_database.py     # Run migrations
python tests/test_quotation_flow.py    # Run tests
python -m uvicorn app.main:app --reload  # Start server

# Frontend
npm install                     # Install dependencies
npm run dev                     # Start dev server
npm run build                   # Build for production
npm run preview                 # Preview production build

# Database
sqlcmd -S SERVER\INSTANCE      # Connect to SQL Server
python scripts/populate_*.py   # Populate test data
```

### Port Reference

| Service | Port | URL |
|---------|------|-----|
| Ollama | 11434 | http://localhost:11434 |
| Backend API | 8000 | http://localhost:8000 |
| Frontend | 5173 | http://localhost:5173 |
| SQL Server | 1433 | - |

---

## Next Steps

1. ✅ Complete setup (this guide)
2. ✅ Verify all services running
3. ✅ Test login and features
4. ✅ Run test scripts
5. 📖 Read feature documentation:
   - `backend/QUOTATION_FEATURE.md`
   - `backend/PRICING_GUIDE.md`
   - `backend/README.md`
   - `frontend/README.md`

---

## Support

- **Backend Issues**: Check `backend/README.md`
- **Frontend Issues**: Check `frontend/README.md`
- **Testing**: Check `backend/tests/README.md`
- **Contact**: rshashidhar513@gmail.com

---

**Last Updated**: August 22, 2026
