# IronOre CRM - Quick Start Guide

Run the project locally without Docker.

## Prerequisites

### Required
- Python 3.8+ (for backend)
- Node.js 14+ (for frontend)
- MSSQL Server or Azure SQL Database
- Git

### Optional
- SQL Server Management Studio (SSMS) for database management
- Ollama (for AI/ML features)

## Setup Steps

### 1. Backend Setup

#### 1a. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 1b. Configure Database

Edit `backend/.env` and set your database connection:

```env
DATABASE_URL=mssql+pyodbc://sa:password@localhost:1433/ironore_crm?driver=ODBC+Driver+18+for+SQL+Server
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-change-this
```

#### 1c. Initialize Database (First Time Only)

Run the setup scripts manually:

```bash
# Connect to your MSSQL server and run these scripts in order:
# 1. Create tables and schema (varies by your database setup)
# 2. Run any SQL scripts in backend/database/ folder

# Or use Python to auto-initialize:
cd backend
python -c "from app.database_setup import init_db; init_db()"
```

#### 1d. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at: **http://localhost:8000**
Swagger UI Docs: **http://localhost:8000/docs**

### 2. Frontend - Chat Widget Setup

The chat widget is a standalone component in `frontend-chat/`.

#### 2a. Install Dependencies

```bash
cd frontend-chat
npm install
```

#### 2b. Start Dev Server

```bash
npm run dev
```

Or for production build:

```bash
npm run build
```

Chat widget will be available at: **http://localhost:5173**

### 3. Frontend - Dashboard Setup (Optional)

Full React dashboard for admin users.

#### 3a. Install Dependencies

```bash
cd frontend
npm install
```

#### 3b. Create .env File

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
VITE_API_URL=http://localhost:8000
```

#### 3c. Start Dev Server

```bash
npm run dev
```

Dashboard will be available at: **http://localhost:5173**

---

## Full Setup (All Services)

Run all three services simultaneously:

### Terminal 1 - Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Chat Frontend

```bash
cd frontend-chat
npm run dev
```

### Terminal 3 - Dashboard (Optional)

```bash
cd frontend
npm run dev
```

---

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | http://localhost:8000 | REST API server |
| API Docs | http://localhost:8000/docs | Swagger UI documentation |
| Chat Widget | http://localhost:5173 | Standalone chat component |
| Dashboard | http://localhost:5173 | Full admin dashboard |

---

## Project Structure

```
ironore-crm/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Request/response schemas
│   │   ├── auth.py            # Authentication logic
│   │   ├── routers/           # API endpoints
│   │   │   ├── chat.py
│   │   │   ├── product.py
│   │   │   ├── customer.py
│   │   │   ├── order.py
│   │   │   └── ...
│   │   └── ...
│   ├── database/              # SQL scripts for initialization
│   ├── .env                   # Environment variables
│   └── requirements.txt       # Python dependencies
│
├── frontend-chat/             # Chat floating button component
│   ├── ChatFloatingButton.jsx # Main component
│   ├── ChatMessage.jsx        # Message component
│   ├── chat-button.css        # Styles
│   ├── package.json
│   └── README.md              # Integration guide
│
└── frontend/                  # Full React dashboard
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   ├── pages/
    │   └── styles.css
    ├── package.json
    ├── vite.config.js
    └── .env.example
```

---

## Database Connection

### MSSQL Server Connection String

Replace values in `backend/.env`:

```env
DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost:1433/ironore_crm?driver=ODBC+Driver+18+for+SQL+Server
```

### Connection Test

```bash
# Test from backend folder
python -c "from app.database import engine; print(engine.connect())"
```

---

## Common Commands

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload

# Run with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Format code
black app/
```

### Frontend-Chat

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Frontend-Dashboard

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

---

## Troubleshooting

### Backend won't start

**Error: ModuleNotFoundError**
```bash
# Install/upgrade dependencies
pip install -r requirements.txt --upgrade
```

**Error: Database connection failed**
```bash
# Check database URL in .env
# Verify MSSQL server is running
# Test connection manually:
python -c "from app.database import engine; print(engine.connect())"
```

### Frontend won't start

**Error: Port 5173 already in use**
```bash
# Use different port
npm run dev -- --port 5174
```

**Error: Dependencies not found**
```bash
# Clear node_modules and reinstall
rm -r node_modules package-lock.json
npm install
```

**Error: API calls failing**
- Check `VITE_API_URL` in `.env` matches backend URL
- Verify backend is running at http://localhost:8000
- Check browser console for CORS errors

### Database issues

**Error: ODBC driver not found**
- Windows: Install "ODBC Driver 18 for SQL Server"
- Mac: `brew install msodbcsql18`
- Linux: Follow MS docs for your distribution

**Error: Authentication failed**
- Verify username and password in DATABASE_URL
- Check database exists: `ironore_crm`

---

## Development Tips

### Enable Debug Mode

Set in `backend/.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Live Code Reload

All three services support hot reload:
- Backend: Uvicorn reloads on file changes
- Frontend-Chat: Vite HMR automatically reloads
- Dashboard: Vite HMR automatically reloads

### API Documentation

Interactive Swagger UI available at: http://localhost:8000/docs

Try API endpoints directly from the browser!

### Browser DevTools

Press F12 in browser to open DevTools:
- **Console**: Check for JavaScript errors
- **Network**: Monitor API calls
- **Application**: View local storage and session data

---

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=               # MSSQL connection string
DEBUG=true                  # Debug mode
LOG_LEVEL=INFO              # Logging level
SECRET_KEY=your-secret-key  # JWT secret key
CORS_ORIGINS=["*"]          # CORS allowed origins
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

---

## Next Steps

1. ✅ Start backend: `cd backend && uvicorn app.main:app --reload`
2. ✅ Start frontend: `cd frontend-chat && npm run dev`
3. ✅ Access chat: http://localhost:5173
4. ✅ Test API: http://localhost:8000/docs

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review API docs at http://localhost:8000/docs
3. Check backend logs for errors
4. Check browser console for frontend errors
5. Contact development team

---

**Happy coding!** 🚀
