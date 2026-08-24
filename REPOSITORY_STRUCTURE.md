# Iron Ore CRM - Repository Structure

Complete guide to the repository organization and file layout.

## 📂 Directory Tree

```
ironore-crm/
│
├── 📄 README.md                          # Main project documentation
├── 📄 PROJECT_OVERVIEW.md                # Detailed project overview
├── 📄 SETUP_GUIDE.md                     # Installation & setup instructions
├── 📄 REPOSITORY_STRUCTURE.md            # This file
├── 📄 VOICE_AND_ENV_SETUP.md             # Voice & environment configuration
├── 📄 .gitignore                         # Git ignore rules
│
│
├── 📁 backend/                           # FastAPI Backend Application
│   ├── 📄 README.md                      # Backend documentation
│   ├── 📄 requirements.txt               # Python dependencies
│   ├── 📄 .env                           # Environment variables (gitignored)
│   ├── 📄 .env.example                   # Environment template
│   │
│   ├── 📁 app/                           # Main application package
│   │   ├── 📄 __init__.py                # Package initializer
│   │   ├── 📄 main.py                    # FastAPI application entry point
│   │   ├── 📄 config.py                  # Configuration & settings
│   │   ├── 📄 database.py                # Database connection & session
│   │   ├── 📄 models.py                  # SQLAlchemy ORM models
│   │   ├── 📄 schemas.py                 # Pydantic request/response schemas
│   │   ├── 📄 auth.py                    # Authentication & JWT logic
│   │   ├── 📄 intent.py                  # Intent classification enums
│   │   ├── 📄 seed_data.py               # Database seed data
│   │   ├── 📄 ollama_client.py           # Ollama AI integration
│   │   ├── 📄 quotation_service.py       # Quotation generation & PDF logic
│   │   │
│   │   └── 📁 routers/                   # API endpoint routers
│   │       ├── 📄 __init__.py
│   │       ├── 📄 auth.py                # Authentication endpoints
│   │       ├── 📄 chat.py                # Chat & intent handling
│   │       ├── 📄 customer.py            # Customer management
│   │       ├── 📄 product.py             # Product information
│   │       ├── 📄 order.py               # Order management
│   │       ├── 📄 complaint.py           # Complaint handling
│   │       ├── 📄 quotation.py           # Quotation endpoints
│   │       ├── 📄 notification.py        # Notifications
│   │       └── 📁 __pycache__/           # Python cache (gitignored)
│   │
│   ├── 📁 database/                      # Database schemas & migrations
│   │   ├── 📄 add_complaint_columns.sql
│   │   ├── 📄 create_quotations_table.sql
│   │   └── 📄 *.sql                      # Other migration scripts
│   │
│   ├── 📁 scripts/                       # Utility & maintenance scripts
│   │   ├── 📄 migrate_database.py        # Database migration runner
│   │   ├── 📄 populate_inventory_data.py # Populate sample products
│   │   ├── 📄 populate_complaint.py      # Add test complaints
│   │   ├── 📄 check_inventory_schema.py  # Verify database schema
│   │   ├── 📄 update_complaint_summaries.py
│   │   ├── 📄 update_one_complaint.py
│   │   ├── 📄 update_specific_complaint.py
│   │   ├── 📄 test_ollama_direct.py      # Test Ollama integration
│   │   ├── 📄 test_ollama_complaint.py   # Test AI complaint generation
│   │   └── 📁 __pycache__/               # Python cache (gitignored)
│   │
│   ├── 📁 tests/                         # Test scripts
│   │   ├── 📄 README.md                  # Testing documentation
│   │   ├── 📄 test_quotation_flow.py     # E2E quotation test
│   │   ├── 📄 test_email_feature.py      # Email contact feature test
│   │   └── 📄 (add more tests here)
│   │
│   ├── 📁 quotations/                    # Generated quotation PDFs (gitignored)
│   │   └── 📄 QT-YYYY-MM-XXX_*.pdf       # Generated quotation files
│   │
│   ├── 📄 QUOTATION_FEATURE.md           # Quotation system documentation
│   ├── 📄 PRICING_GUIDE.md               # Pricing logic documentation
│   └── 📁 __pycache__/                   # Python cache (gitignored)
│
│
├── 📁 frontend/                          # React + Vite Frontend Application
│   ├── 📄 README.md                      # Frontend documentation
│   ├── 📄 package.json                   # npm dependencies
│   ├── 📄 package-lock.json              # Locked dependencies
│   ├── 📄 vite.config.js                 # Vite build configuration
│   ├── 📄 index.html                     # HTML entry point
│   ├── 📄 .env                           # Environment variables (gitignored)
│   ├── 📄 .env.example                   # Environment template
│   │
│   ├── 📁 src/                           # Source code
│   │   ├── 📄 main.jsx                   # Vite entry point
│   │   ├── 📄 App.jsx                    # Root React component
│   │   ├── 📄 api.js                     # API client utilities
│   │   ├── 📄 styles.css                 # Global CSS styles
│   │   │
│   │   ├── 📁 components/                # Reusable React components
│   │   │   ├── 📄 ChatWidget.jsx         # Main chat interface
│   │   │   ├── 📄 ChatMessage.jsx        # Individual message display
│   │   │   ├── 📄 ProductCard.jsx        # Product card component
│   │   │   └── 📁 __pycache__/           # Python cache (gitignored)
│   │   │
│   │   └── 📁 pages/                     # Page components
│   │       ├── 📄 Login.jsx              # Login page
│   │       └── 📄 Dashboard.jsx          # Main dashboard page
│   │
│   ├── 📁 public/                        # Static assets
│   │   └── 📄 (favicon, logos, etc.)
│   │
│   ├── 📁 node_modules/                  # npm packages (gitignored)
│   │   └── (dependencies installed here)
│   │
│   └── 📁 dist/                          # Production build (gitignored)
│       └── (generated on npm run build)
│
│
└── 📁 .git/                              # Git repository data
    └── (git history and objects)
```

---

## 📋 File Descriptions

### Root Level Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main project readme with feature overview |
| `PROJECT_OVERVIEW.md` | Detailed project architecture and design |
| `SETUP_GUIDE.md` | Step-by-step installation instructions |
| `REPOSITORY_STRUCTURE.md` | This file - directory organization |
| `VOICE_AND_ENV_SETUP.md` | Voice input and environment setup |
| `.gitignore` | Git ignore rules (PDFs, cache, env files) |

---

### Backend Application

#### Core Application Files (`app/`)

| File | Purpose | Key Functions |
|------|---------|---|
| `main.py` | FastAPI application | App initialization, route includes, CORS setup |
| `config.py` | Settings & configuration | Load env vars, app settings |
| `database.py` | Database connection | Session management, engine setup |
| `models.py` | ORM models | LoginMaster, CustomerMaster, ProductMaster, etc. |
| `schemas.py` | Request/Response schemas | Pydantic models for validation |
| `auth.py` | Authentication logic | JWT generation, password hashing |
| `intent.py` | Intent enums | GREETING, COMPLAINT, ORDER_REQUEST, etc. |
| `seed_data.py` | Sample data | Test users, products, inventory |
| `ollama_client.py` | AI integration | Ollama API client, prompt generation |
| `quotation_service.py` | Quotation logic | PDF generation, pricing, numbering |

#### API Routers (`app/routers/`)

| File | Endpoints | Purpose |
|------|-----------|---------|
| `auth.py` | `/api/auth/*` | Login, logout, token verification |
| `chat.py` | `/api/chat` | Main chat endpoint, intent classification |
| `customer.py` | `/api/customer/*` | Customer profile, orders, complaints |
| `product.py` | `/api/product/*` | Product list, details, categories |
| `order.py` | `/api/order/*` | Create, get, list orders |
| `complaint.py` | `/api/complaint/*` | Create, get, track complaints |
| `quotation.py` | `/api/quotation/*` | Create, get quotations |
| `notification.py` | `/api/notification/*` | Alerts and notifications |

#### Database Files (`database/`)

| File | Purpose |
|------|---------|
| `add_complaint_columns.sql` | Add complaint tracking columns |
| `create_quotations_table.sql` | Create QuotationMaster table |
| `*.sql` | Other migration scripts |

#### Utility Scripts (`scripts/`)

| File | Purpose |
|------|---------|
| `migrate_database.py` | Run all SQL migrations |
| `populate_inventory_data.py` | Add sample products & inventory |
| `populate_complaint.py` | Add test complaints |
| `check_inventory_schema.py` | Verify database structure |
| `update_*.py` | Data update utilities |
| `test_*.py` | Quick test scripts |

#### Test Scripts (`tests/`)

| File | Purpose |
|------|---------|
| `README.md` | Testing documentation |
| `test_quotation_flow.py` | E2E quotation workflow test |
| `test_email_feature.py` | Email contact feature test |

#### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Backend architecture & API |
| `QUOTATION_FEATURE.md` | Quotation system details |
| `PRICING_GUIDE.md` | Pricing calculation logic |

---

### Frontend Application

#### React Components

| File | Purpose | Props |
|------|---------|-------|
| `App.jsx` | Root component | - |
| `ChatWidget.jsx` | Main chat interface | user, open, onToggle |
| `ChatMessage.jsx` | Message display | role, text, intent-specific props |
| `ProductCard.jsx` | Product display | product, onSelect |

#### Pages

| File | Purpose | Route |
|------|---------|-------|
| `Login.jsx` | User authentication | / |
| `Dashboard.jsx` | Main interface | /dashboard |

#### Utilities

| File | Purpose |
|------|---------|
| `api.js` | API client wrapper, error handling |
| `main.jsx` | Vite entry point |
| `styles.css` | Global CSS variables and styles |

#### Configuration

| File | Purpose |
|------|---------|
| `vite.config.js` | Vite build configuration |
| `package.json` | Dependencies and scripts |
| `.env.example` | Environment template |

---

## 🔄 File Organization Logic

### Backend Organization

```
app/              → Core application code
  routers/        → API endpoints (grouped by feature)
  models.py       → Database models
  schemas.py      → Request/response validation
  main.py         → Application entry point

database/         → SQL migration scripts
scripts/          → Utility & data scripts
tests/            → Test scripts
quotations/       → Generated PDF outputs
```

### Frontend Organization

```
src/              → Source code
  components/     → Reusable UI components
  pages/          → Full page components
  api.js          → API client
  App.jsx         → Root component
  styles.css      → Global styles

public/           → Static assets
dist/             → Production build (generated)
node_modules/     → Dependencies (generated)
```

---

## 📊 File Statistics

### Backend
- **Total Python files**: 20+
- **API endpoints**: 8 routers
- **Database tables**: 8+ tables
- **Documentation files**: 3
- **Test files**: 2
- **Lines of code**: 5,000+

### Frontend
- **React components**: 5+
- **Pages**: 2
- **CSS files**: 1
- **Documentation files**: 1
- **Lines of code**: 2,000+

### Documentation
- **README files**: 4
- **Setup guides**: 1
- **Architecture docs**: 2
- **Feature docs**: 2
- **Total documentation**: 15+ pages

---

## 🔐 Files That Require Attention

### Sensitive Files (Gitignored)

| File/Dir | Reason |
|----------|--------|
| `.env` | Contains passwords and API keys |
| `__pycache__/` | Compiled Python cache |
| `node_modules/` | Large dependency directory |
| `dist/` | Generated build output |
| `quotations/` | Generated PDF files |
| `*.pdf` | Generated documents |

### Configuration Files

| File | Environment |
|------|-------------|
| `.env` | Local development (gitignored) |
| `.env.example` | Template for setup |

---

## 🚀 Key Entry Points

### Backend
- **Start**: `python -m uvicorn app.main:app --reload`
- **Tests**: `python tests/test_*.py`
- **Database**: `python scripts/migrate_database.py`

### Frontend
- **Start**: `npm run dev`
- **Build**: `npm run build`
- **Preview**: `npm run preview`

---

## 📈 Scalability Considerations

### Adding New Features

1. **New API Endpoint**:
   - Create file in `backend/app/routers/`
   - Add models/schemas in `app/models.py` or `app/schemas.py`
   - Include in `app/main.py`

2. **New Intent**:
   - Add to `app/intent.py`
   - Create handler in `app/routers/chat.py`
   - Test with new script

3. **New Component**:
   - Create in `frontend/src/components/`
   - Import in pages or other components
   - Style in `styles.css` or inline

4. **New Database Table**:
   - Add model in `app/models.py`
   - Create migration in `database/`
   - Run migration script

---

## 🔗 File Dependencies

### Critical Dependencies

```
app/main.py
  ├── app/routers/* (all routers)
  ├── app/database.py
  ├── app/config.py
  └── app/models.py

app/routers/chat.py
  ├── app/ollama_client.py
  ├── app/intent.py
  ├── app/models.py
  └── app/quotation_service.py

frontend/App.jsx
  ├── components/ChatWidget.jsx
  ├── pages/Login.jsx
  ├── pages/Dashboard.jsx
  └── api.js
```

---

## 📝 Maintenance Notes

### Regular Tasks

1. **Backup Important Files**:
   - `.env` (store credentials securely)
   - Database backups
   - Generated quotations

2. **Clean Generated Files**:
   - `backend/quotations/*.pdf` (safe to delete)
   - `frontend/dist/` (regenerate with build)
   - `backend/__pycache__/` (automatically cleaned)

3. **Update Dependencies**:
   - Backend: `pip install --upgrade -r requirements.txt`
   - Frontend: `npm update`

---

## 🎯 Quick Navigation

- **Setup**: Start with `SETUP_GUIDE.md`
- **Architecture**: See `PROJECT_OVERVIEW.md`
- **Backend API**: See `backend/README.md`
- **Frontend**: See `frontend/README.md`
- **Testing**: See `backend/tests/README.md`
- **Features**: See `backend/QUOTATION_FEATURE.md`

---

**Last Updated**: August 22, 2026
**Version**: 1.0.0
