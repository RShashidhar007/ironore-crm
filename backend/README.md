# Iron Ore CRM - Backend

FastAPI-based backend for the Iron Ore CRM system with AI-powered chat, quotation generation, complaint tracking, and order management.

## 📁 Project Structure

```
backend/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration & environment variables
│   ├── database.py               # Database connection & session management
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── auth.py                   # Authentication & JWT handling
│   ├── intent.py                 # Intent classification enums
│   ├── ollama_client.py          # Ollama AI integration
│   ├── quotation_service.py      # Quotation generation & PDF logic
│   ├── seed_data.py              # Database seed data
│   └── routers/                  # API endpoint routers
│       ├── auth.py               # Authentication endpoints
│       ├── chat.py               # Chat/intent handling endpoints
│       ├── customer.py           # Customer management
│       ├── product.py            # Product information
│       ├── order.py              # Order management
│       ├── complaint.py          # Complaint handling
│       ├── quotation.py          # Quotation endpoints
│       └── notification.py       # Notification endpoints
├── database/                     # Database schemas & migrations
│   └── *.sql                     # Migration scripts
├── scripts/                      # Utility & maintenance scripts
│   ├── migrate_database.py       # Database migration runner
│   ├── populate_*.py             # Data population scripts
│   ├── update_*.py               # Data update scripts
│   └── check_*.py                # Database verification scripts
├── tests/                        # Test scripts
│   ├── test_quotation_flow.py   # End-to-end quotation test
│   ├── test_email_feature.py    # Email feature test
│   └── README.md                # Testing documentation
├── quotations/                   # Generated quotation PDFs (output)
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
├── QUOTATION_FEATURE.md         # Quotation feature documentation
├── PRICING_GUIDE.md             # Pricing logic documentation
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- SQL Server 2019 or later
- Ollama (for AI chat features)
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RShashidhar007/ironore-crm.git
   cd ironore-crm/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

5. **Run database migrations:**
   ```bash
   python scripts/migrate_database.py
   ```

6. **Start the server:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Available Endpoints

#### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/verify` - Verify token

#### Chat (Main Feature)
- `POST /chat` - Send message and get AI response
  - Supports: Complaints, Quotations, Orders, Product Info, etc.

#### Quotations
- `POST /quotation/create` - Create new quotation
- `GET /quotation/{id}` - Get quotation details
- `GET /quotation/customer/{cid}` - Get customer quotations

#### Orders
- `POST /order/create` - Create new order
- `GET /order/{id}` - Get order details

#### Complaints
- `POST /complaint/create` - Create complaint
- `GET /complaint/{id}` - Get complaint details
- `GET /complaint/track/{id}` - Track complaint status

#### Products
- `GET /product/list` - Get all products
- `GET /product/{pid}` - Get product details

#### Customer
- `GET /customer/profile` - Get customer profile
- `GET /customer/orders` - Get customer orders
- `GET /customer/complaints` - Get customer complaints

---

## 🔄 Main Features

### 1. AI-Powered Chat (`/api/chat`)
Intelligent conversation with intent classification:
- **GREETING** - Welcome message
- **PRODUCT_INFORMATION** - Product details
- **ORDER_REQUEST** - Place orders
- **QUOTATION_REQUEST** - Generate quotations
- **COMPLAINT** - Raise complaints
- **COMPLAINT_TRACKING** - Track complaint status
- **WHATSAPP_CONTACT** - Company contact info

### 2. Quotation Generation
- Automatic quotation number generation
- Price calculation based on last 2-3 sales
- PDF generation with ReportLab
- Email integration ready

**Workflow:**
```
Customer clicks "Ask for Quotation"
    ↓
Select product from list
    ↓
Enter quantity (MT)
    ↓
System generates quotation with:
  - Product details
  - Quantity
  - Price per MT (avg of last 3 sales)
  - Total amount
  - Validity period (7 days)
  - PDF file
```

### 3. Order Management
- Product availability checking
- Order tracking
- Inventory integration

### 4. Complaint Management
- Multiple complaint categories
- Status tracking
- Historical complaint viewing
- PO and dispatch date tracking

### 5. Contact Company Feature
- Email contact display from .env
- Mailto link integration
- Support phone and WhatsApp info

---

## 🔐 Authentication

Uses JWT (JSON Web Tokens) for security:

1. **Login:** Send credentials → Receive JWT token
2. **API Calls:** Include token in `Authorization` header
   ```
   Authorization: Bearer <token>
   ```
3. **Token Expiry:** 120 minutes (configurable)

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Database
DB_MODE=mssql
MSSQL_SERVER=localhost\SQLEXPRESS
MSSQL_DATABASE=Customer_DB
MSSQL_USER=crm_user
MSSQL_PASSWORD=your_password

# Authentication
JWT_SECRET=your-random-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120

# AI Chat
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_ENABLED=true
OLLAMA_TIMEOUT_SECONDS=120

# Company Info
COMPANY_WHATSAPP_NUMBER=7022486778
COMPANY_SUPPORT_EMAIL=rshashidhar513@gmail.com
COMPANY_SUPPORT_PHONE=7022486778

# Frontend
FRONTEND_ORIGIN=http://localhost:5173
```

---

## 🧪 Testing

Run test scripts to verify features:

```bash
# Test quotation workflow
python tests/test_quotation_flow.py

# Test email feature
python tests/test_email_feature.py
```

See `tests/README.md` for detailed testing documentation.

---

## 📊 Database Schema

### Key Tables

- **LoginMaster** - User accounts and authentication
- **CustomerMaster** - Customer information
- **ProductMaster** - Product catalog
- **InventoryMaster** - Product inventory and pricing
- **ComplaintMaster** - Complaint records
- **QuotationMaster** - Generated quotations
- **OrderMaster** - Customer orders
- **NotificationMaster** - System notifications

---

## 🛠️ Utility Scripts

### Database Management

```bash
# Migrate database
python scripts/migrate_database.py

# Populate inventory data
python scripts/populate_inventory_data.py

# Check database schema
python scripts/check_inventory_schema.py

# Update complaint summaries
python scripts/update_complaint_summaries.py
```

---

## 📄 Documentation Files

- **`QUOTATION_FEATURE.md`** - Detailed quotation generation logic
- **`PRICING_GUIDE.md`** - Pricing calculation methodology
- **`tests/README.md`** - Testing guide

---

## 🐛 Troubleshooting

### Database Connection Issues
```python
# Error: "Could not connect to SQL Server"
# Solutions:
1. Check MSSQL_SERVER in .env
2. Verify SQL Server is running
3. Check credentials are correct
4. Check firewall settings
```

### Ollama Not Connecting
```python
# Error: "Failed to connect to Ollama"
# Solutions:
1. Start Ollama: ollama serve
2. Pull model: ollama pull llama3.2
3. Check OLLAMA_BASE_URL in .env
4. Verify port 11434 is accessible
```

### JWT Token Issues
```python
# Error: "Invalid token"
# Solutions:
1. Ensure token is in Authorization header
2. Check token hasn't expired
3. Verify JWT_SECRET matches
4. Re-login to get new token
```

---

## 📦 Dependencies

Key packages:
- **fastapi** - Web framework
- **sqlalchemy** - ORM
- **pydantic** - Data validation
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **requests** - HTTP client
- **reportlab** - PDF generation
- **python-dotenv** - Environment variables
- **pyodbc** - SQL Server driver

Full list: See `requirements.txt`

---

## 🔗 Related Documentation

- **Frontend:** See `../frontend/README.md`
- **Project Root:** See `../README.md`

---

## 📝 Development Guidelines

### Code Structure
- Follow FastAPI best practices
- Use SQLAlchemy for database queries
- Implement error handling with try-except
- Log important operations
- Add docstrings to functions

### Adding New Endpoints
1. Create router file in `routers/`
2. Define request/response schemas
3. Implement endpoint function
4. Include in `app/main.py`
5. Add error handling
6. Document in README

### Adding New Intent
1. Add intent to `app/intent.py`
2. Add handler in `app/routers/chat.py`
3. Map action in `ACTION_TO_INTENT`
4. Create test script
5. Document the flow

---

## 🚀 Deployment

### For Production
1. Set `OLLAMA_ENABLED=false` if using API-only mode
2. Update `JWT_SECRET` with strong random key
3. Configure proper CORS origins
4. Use environment-specific `.env`
5. Enable SQL Server SSL
6. Run migrations
7. Start with gunicorn/uvicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app.main:app"
```

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review test scripts
3. Check logs for errors
4. Refer to documentation files
5. Contact: rshashidhar513@gmail.com

---

**Last Updated:** August 22, 2026
**Version:** 1.0.0
