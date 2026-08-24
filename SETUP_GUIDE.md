# Iron Ore CRM - Setup Guide

## Prerequisites

- Python 3.8+
- SQL Server (or SQLite for development)
- Node.js 14+ (for frontend)
- npm or yarn

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (web framework)
- SQLAlchemy (ORM)
- Pydantic (validation)
- ReportLab (PDF generation) ← **New for quotations**
- Pillow (image handling) ← **New for PDF**
- PyODBC (SQL Server driver)
- And other dependencies

### 4. Configure Environment

Create `.env` file in `backend/` directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` with your settings:
```
DB_MODE=mssql  # or sqlite for local testing
DB_SERVER=your_server
DB_NAME=Customer_DB
DB_USER=your_username
DB_PASSWORD=your_password

FRONTEND_ORIGIN=http://localhost:5173
COMPANY_SUPPORT_EMAIL=sales@company.com
COMPANY_WHATSAPP_NUMBER=+91XXXXXXXXXX

# Ollama settings (optional)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
```

### 5. Database Setup

#### Option A: SQL Server (Production)
```bash
# Apply migrations
sqlcmd -S your_server -U username -P password -d Customer_DB -i database/create_quotations_table.sql
```

#### Option B: SQLite (Development)
```bash
# Set DB_MODE=sqlite in .env
# Tables are created automatically on first run
```

### 6. Run Backend Server

```bash
# Development (with hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test API:**
```bash
curl http://localhost:8000/api/health
# Response: {"status":"ok"}
```

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Configure Environment

Create `.env` file in `frontend/` directory:

```
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME="Iron Ore CRM"
```

### 4. Run Development Server

```bash
npm run dev
# or
yarn dev
```

**Expected Output:**
```
VITE v4.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

## Verification Checklist

### Backend
- [ ] Dependencies installed: `pip list | grep -i reportlab`
- [ ] App loads: `python -c "from app.main import app; print('✓ OK')"`
- [ ] Database connects
- [ ] Server runs: `uvicorn app.main:app --reload`
- [ ] Health endpoint responds: `curl http://localhost:8000/api/health`

### Frontend
- [ ] Dependencies installed: `npm list`
- [ ] Dev server runs: `npm run dev`
- [ ] Page loads: `http://localhost:5173`
- [ ] Can login

### Integration
- [ ] Frontend connects to backend API
- [ ] Chat functionality works
- [ ] Can click "Ask for a Quotation"
- [ ] Quotation PDF generates

## Important Dependencies for Quotations

The quotation feature requires two new packages:

### ReportLab 4.0.9
- PDF document generation library
- Professional reporting capabilities
- Used to create branded quotation PDFs

### Pillow 10.1.0
- Python Imaging Library
- Image handling and processing
- Required by ReportLab for PDF graphics

Both are automatically installed with `pip install -r requirements.txt`

## Troubleshooting

### "ModuleNotFoundError: No module named 'reportlab'"
**Solution:** Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### "ModuleNotFoundError: No module named 'app'"
**Solution:** Run from `backend/` directory with Python path
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### "Connection refused" to database
**Solution:** Check DB_MODE in `.env`
- For SQL Server: Verify server/credentials
- For SQLite: Ensure database file permissions

### PDF not generating / "Permission denied"
**Solution:** Create `quotations/` directory with write permissions
```bash
mkdir quotations
chmod 755 quotations  # Linux/Mac
# Windows: Right-click folder → Properties → Security → Edit
```

### CORS errors in frontend
**Solution:** Check `FRONTEND_ORIGIN` in backend `.env`
```
FRONTEND_ORIGIN=http://localhost:5173
```

### API calls failing from frontend
**Solution:** Check `VITE_API_URL` in frontend `.env`
```
VITE_API_URL=http://localhost:8000/api
```

## Database Migrations

### Create Quotations Table
```bash
# SQL Server
sqlcmd -S SERVER -U USER -P PASS -d DB -i backend/database/create_quotations_table.sql

# Via Python
python backend/scripts/migrate_database.py
```

### Verify Table Created
```sql
SELECT * FROM [dbo].[Quotations_Master]
```

## Project Structure

```
ironore-crm/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app
│   │   ├── models.py                # Database models (includes Quotation)
│   │   ├── quotation_service.py     # Quotation logic
│   │   └── routers/
│   │       ├── chat.py              # Chat endpoints
│   │       └── quotation.py         # Quotation endpoints
│   ├── database/
│   │   ├── create_quotations_table.sql
│   │   └── seed_inventory_data.sql
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Example configuration
│   └── .env                         # Local configuration (git-ignored)
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── api.js
│   ├── package.json                 # Node dependencies
│   ├── .env.example                 # Example configuration
│   └── .env                         # Local configuration (git-ignored)
│
└── README.md                        # Main documentation
```

## Development Workflow

### 1. Start Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

### 2. Start Frontend (in new terminal)
```bash
cd frontend
npm run dev
```

### 3. Access Application
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Make Changes
- Backend: Changes auto-reload
- Frontend: Changes auto-reload

### 5. Test Quotation Feature
- Login to frontend
- Click "Ask for a Quotation"
- Enter product ID (e.g., 13000000) and quantity (e.g., 100)
- See generated quotation with PDF

## Testing

### Backend Tests
```bash
cd backend
pytest tests/  # If tests exist
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Manual Testing
1. Test each API endpoint (see API docs at http://localhost:8000/docs)
2. Test chat flow in frontend
3. Test quotation generation with multiple products
4. Verify PDF downloads correctly

## Production Deployment

### Backend
1. Install dependencies: `pip install -r requirements.txt`
2. Set up database: Run migration scripts
3. Configure `.env` for production
4. Run with gunicorn: `gunicorn app.main:app -w 4`

### Frontend
1. Build: `npm run build`
2. Deploy built files to web server
3. Configure `.env` for production API URL

## Support

For issues or questions:
- Check documentation in `backend/` and root directories
- Review error messages carefully
- Verify all dependencies are installed
- Ensure `.env` files are properly configured

---

**Last Updated:** August 2026  
**Version:** 1.0
