# CRM Bot — Iron Ore / Iron Pellet Customer Portal

A complete, working CRM chatbot system:

```
Customer → React/Vite Frontend → FastAPI Backend → Ollama and/or SQL Server → FastAPI Backend → React/Vite Frontend → Customer
```

- **Frontend**: React + Vite — login screen, customer dashboard, floating chatbot.
- **Backend**: FastAPI — auth, authorization, DB access, intent routing, Ollama integration.
- **LLM**: Ollama (local) — phrases customer-friendly replies from backend-verified data only.
- **Database**: Microsoft SQL Server (production) or SQLite (local demo) — seamlessly switch via config.

The bot only knows about the six tables that currently exist (`Login_Master`, `Customer_Detail`,
`Product_Master`, `ProductCategory_Master`, `IronOreSpecification_Master`,
`IronPelletSpecification_Master`). It never invents orders, quotations, inventory levels,
dispatch info, or complaint numbers — those modules are explicitly reported as "not yet
available" until matching tables are added.

---

## 1. Quick start (local demo, no SQL Server needed)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # defaults to DB_MODE=sqlite — nothing else required
python -m app.seed_data          # creates customer_db.sqlite3 with demo data
uvicorn app.main:app --reload --port 8000
```

Demo login: **user ID** `shashi` / **password** `shashi@1234`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env             # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`).

### Ollama (optional but recommended)

```bash
ollama pull llama3.1
ollama serve
```

If Ollama isn't running, the backend automatically falls back to clean templated
responses built directly from the verified database data — **the bot keeps working
either way**, it just loses the extra natural-language polish.

---

## 2. Switching to MS SQL Server

**📚 See detailed guide: [`backend/MSSQL_QUICKSTART.md`](backend/MSSQL_QUICKSTART.md) (5-minute setup)**

### Quick Setup

1. **Install ODBC Driver 18 for SQL Server**
   - Download: https://go.microsoft.com/fwlink/?linkid=2249004
   - Verify: `Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}`

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt  # Now includes pyodbc
   ```

3. **Create database**
   ```bash
   sqlcmd -S localhost -U sa -P "YourPassword" -Q "CREATE DATABASE Customer_DB"
   ```

4. **Configure `.env`**
   ```env
   DB_MODE=mssql
   MSSQL_SERVER=localhost
   MSSQL_PORT=1433
   MSSQL_DATABASE=Customer_DB
   MSSQL_USER=sa
   MSSQL_PASSWORD=YourPassword123!
   MSSQL_DRIVER=ODBC Driver 18 for SQL Server
   MSSQL_ENCRYPT=yes
   MSSQL_TRUST_SERVER_CERT=yes
   ```

5. **Test connection & create tables**
   ```bash
   python test_connection.py        # Verify connection works
   python create_mssql_schema.py    # Create all tables
   python -m app.seed_data          # Optional: Load demo data
   ```

6. **Start the backend**
   ```bash
   uvicorn app.main:app --reload
   ```

**📖 Resources:**
- Quick Start: `backend/MSSQL_QUICKSTART.md`
- Comprehensive Guide: `MSSQL_SETUP_GUIDE.md`
- Migration Summary: `backend/MSSQL_MIGRATION_SUMMARY.md`

Passwords in `Login_Master` must be bcrypt hashes (use `app.auth.hash_password(...)`
to generate one), never plaintext.

---

## 3. Project layout

```
backend/
  app/
    main.py          FastAPI app, CORS, router registration
    config.py         All settings read from environment variables
    database.py        SQLAlchemy engine/session
    models.py            ORM models for the six existing tables ONLY
    schemas.py             Pydantic request/response models
    auth.py                   JWT + bcrypt password verification, current-user dependency
    intent.py                    Rule-based intent classification & entity extraction
    ollama_client.py               Calls local Ollama, fails soft to templated replies
    seed_data.py                    Demo data loader (SQLite only)
    routers/
      auth.py       POST /api/auth/login
      customer.py    GET  /api/customer/me            (authenticated customer only)
      product.py      GET  /api/products, /api/categories, /api/specs/iron-ore, /api/specs/iron-pellet
      chat.py           POST /api/chat                 (core chatbot endpoint)

frontend/
  src/
    api.js              Fetch wrapper + session storage
    App.jsx              Auth-aware router
    pages/
      Login.jsx
      Dashboard.jsx
    components/
      ChatWidget.jsx      Floating button + chat window
      ChatMessage.jsx      Markdown-rendering message bubble
      ProductCard.jsx
    styles.css              Full design system
```

---

## 4. What the bot can and can't do today

| Capability | Status |
|---|---|
| Customer login / authorization | ✅ Backed by `Login_Master`, JWT sessions |
| Customer's own details | ✅ Backed by `Customer_Detail`, scoped to authenticated CID |
| Product info & categories | ✅ Backed by `Product_Master` / `ProductCategory_Master` |
| Iron Ore specifications | ✅ Backed by `IronOreSpecification_Master` |
| Iron Pellet specifications | ✅ Backed by `IronPelletSpecification_Master` |
| Quotation / Order requests | 🟡 Collects details in chat, clearly states no storage/processing exists yet |
| Order tracking / dispatch | 🟡 Clearly states this isn't available yet |
| Inventory quantity | 🟡 Reports product Active/Inactive status only, never a quantity |
| Complaints | 🟡 Collects details in chat, clearly states no permanent registration yet |
| WhatsApp / human support | ✅ if configured via `.env`, otherwise says so honestly |

When Orders, Inventory, Quotations, Dispatch, or Complaints tables are added later,
extend `models.py`, `schemas.py`, add a router, and add matching branches in
`routers/chat.py` / `intent.py` — the rest of the system does not need to change.

---

## 5. Security notes

- The frontend never talks to SQL Server or Ollama directly — only to the FastAPI backend.
- Passwords are bcrypt-hashed; the API never returns password fields.
- Every customer-data endpoint requires a valid JWT resolved to an **active**
  `Login_Master` row (`get_current_user` dependency) before touching the DB.
- A customer can only ever retrieve the `Customer_Detail` row linked to their own login.
- All DB queries go through SQLAlchemy's parameterized query builder — no raw string-built SQL.
- The chat endpoint sanitizes whatever Ollama returns (strips SQL-looking text, credential-shaped
  strings, and any other customer's CID) before it reaches the frontend — Ollama's output is
  treated as untrusted, not as an authority on security rules.
