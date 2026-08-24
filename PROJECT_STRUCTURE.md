# Iron Ore CRM - Project Structure Guide

## Overview
The Iron Ore CRM project is organized for scalability, maintainability, and professional GitHub deployment.

## Directory Organization

### Root Level
```
ironore-crm/
├── README.md                  # Main project documentation
├── VOICE_AND_ENV_SETUP.md    # Voice and environment setup guide
├── PROJECT_STRUCTURE.md      # This file
└── .gitignore               # Git ignore rules
```

### Backend (`backend/`)
```
backend/
├── app/                      # Main application code
│   ├── routers/             # API endpoint handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── chat.py          # Chat assistant endpoints
│   │   ├── complaint.py      # Complaint management endpoints
│   │   ├── customer.py       # Customer information endpoints
│   │   ├── product.py        # Product catalog endpoints
│   │   └── notification.py   # Notification endpoints
│   ├── models.py            # Database ORM models
│   ├── schemas.py           # Request/response schemas
│   ├── auth.py              # Authentication logic
│   ├── database.py          # Database connection management
│   ├── config.py            # Configuration management
│   ├── intent.py            # Intent classification for chat
│   ├── ollama_client.py      # AI/Ollama integration
│   ├── seed_data.py         # Initial data seeding
│   └── __init__.py          # Package initialization
├── database/                # SQL migration scripts
│   ├── add_complaint_columns.sql    # Complaint table schema
│   └── seed_inventory_data.sql      # Inventory sample data
├── scripts/                 # Utility and test scripts
│   ├── populate_inventory_data.py   # Populate inventory
│   ├── populate_complaint.py        # Add test complaints
│   ├── check_inventory_schema.py    # Verify schema
│   ├── check_all_complaints.py      # Review all complaints
│   ├── update_complaint_summaries.py # Update summaries
│   ├── test_ollama_direct.py        # Test AI integration
│   ├── test_ollama_complaint.py     # Test complaint AI
│   └── update_specific_complaint.py # Update single complaint
├── requirements.txt         # Python dependencies
├── migrate_database.py      # Database migration runner
├── .env                     # Environment variables (local only, not in git)
└── .env.example             # Environment template (in git)
```

### Frontend (`frontend/`)
```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatMessage.jsx       # Chat message display
│   │   ├── ChatWidget.jsx        # Chat interface widget
│   │   └── ProductCard.jsx       # Product display card
│   ├── pages/               # Full page components
│   │   ├── Dashboard.jsx         # Main dashboard
│   │   └── Login.jsx             # Login page
│   ├── api.js              # API client helper
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # React entry point
│   └── styles.css          # Global styles
├── public/                 # Static assets
├── package.json            # NPM dependencies and scripts
├── package-lock.json       # Dependency lock file
├── vite.config.js         # Vite build configuration
├── index.html             # HTML entry point
├── .env                   # Environment variables (local only, not in git)
└── .env.example           # Environment template (in git)
```

## File Organization Rationale

### Backend Scripts Organization
- **`database/`**: SQL migration and seed scripts
  - Grouped for easy database setup
  - Can be version controlled
  - Easy to run migrations in sequence

- **`scripts/`**: Utility and testing scripts
  - Kept separate from production code
  - Easy to identify non-core functionality
  - Can be run independently for maintenance

### Environment Configuration
- **`.env`**: Local configuration (NOT in git - ignored)
  - Contains sensitive credentials
  - Database passwords, API keys
  - Personal configuration

- **`.env.example`**: Template (IN git)
  - Shows required environment variables
  - Helps new developers understand setup
  - No sensitive values included

## Git Ignore Strategy

The `.gitignore` file excludes:
```
__pycache__/    # Python cache
*.pyc          # Python compiled files
.venv/         # Virtual environment
*.sqlite3      # SQLite databases
.env           # Environment secrets
node_modules/  # NPM dependencies
dist/          # Build output
.DS_Store      # macOS files
```

This ensures only source code and configuration templates are committed.

## Development Workflow

### Setting Up for Development
1. Clone repository
2. Copy `.env.example` to `.env` in both `backend/` and `frontend/`
3. Fill in local values in `.env` files
4. Install dependencies and run servers

### Before Committing
1. Ensure `.env` files are NOT added (git will ignore them)
2. Update `.env.example` if adding new configuration
3. Don't commit sensitive data
4. Run tests from `scripts/` directory if needed

### Deployment
- Only `.env.example` is in the repository
- Deployment platforms handle `.env` configuration
- All source code properly organized in subdirectories
- Database migrations tracked in `database/` folder

## Key Improvements

✅ **Cleaner Root Directory**: Utility scripts moved to `scripts/`
✅ **Organized Migrations**: SQL files in dedicated `database/` folder
✅ **Secure Configuration**: `.env.example` template prevents secrets exposure
✅ **Better Documentation**: Comprehensive README with setup instructions
✅ **Professional Structure**: Follows Python/JavaScript project conventions
✅ **Easy Onboarding**: Clear organization helps new developers navigate code
✅ **Maintenance Ready**: Utility scripts separated from production code

## Running Scripts

From `backend/` directory:
```bash
# Populate inventory
python scripts/populate_inventory_data.py

# Check inventory schema
python scripts/check_inventory_schema.py

# Add test complaints
python scripts/populate_complaint.py

# Test AI integration
python scripts/test_ollama_direct.py
```

## Database Migration

Run SQL scripts from `database/` folder:
```bash
# In SQL Server Management Studio or command line:
sqlcmd -S your_server -U username -P password -d Customer_DB -i database/add_complaint_columns.sql
```

Or use Python migration runner:
```bash
python migrate_database.py
```

---

Last Updated: August 2026
Structure Version: 1.0
