# Iron Ore CRM - AI-Powered Customer Relationship Management System

An intelligent CRM system for iron ore and pellet product businesses with AI-powered chat support, complaint management, and inventory tracking.

## Features

### 🤖 AI Chat Assistant
- Intelligent chatbot powered by Ollama (LLaMA 3.2)
- Natural language understanding and response generation
- Voice input support for hands-free operation
- Real-time customer interactions

### 📦 Product Management
- Complete product catalog (Iron Ore, Iron Pellets)
- Product specifications and details
- Category-based organization
- Inventory tracking with real-time availability

### 🛒 Order Management
- Smart product selection with availability checking
- Quantity validation against inventory
- Automatic inventory deduction on order acceptance
- Order tracking with status updates

### 🚨 Complaint Management
- Three-tier complaint tracking system:
  - **Under Review**: Initial complaint status
  - **In Progress**: Investigation complete, resolution in 2-3 working days
  - **Resolved**: Complaint resolution delivered
- Automated solution generation using AI
- Root cause analysis tracking
- Corrective action management

### 💬 Communication Features
- Direct email contact option
- Company information display
- Customer support notifications
- Real-time chat messaging

### 🔒 Security
- JWT-based authentication
- Role-based access control
- Secure password hashing
- CORS protection

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Microsoft SQL Server
- **AI**: Ollama (LLaMA 3.2)
- **ORM**: SQLAlchemy
- **Authentication**: JWT

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: CSS3
- **HTTP Client**: Fetch API
- **Markdown**: react-markdown

## Project Structure

```
ironore-crm/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   ├── models.py         # Database models
│   │   ├── schemas.py        # Request/response schemas
│   │   ├── auth.py           # Authentication logic
│   │   ├── database.py       # Database connection
│   │   ├── config.py         # Configuration
│   │   ├── intent.py         # Intent classification
│   │   └── ollama_client.py  # AI integration
│   ├── database/             # SQL migration scripts
│   ├── scripts/              # Utility and test scripts
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment template
│   └── main.py               # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── api.js            # API client
│   │   ├── App.jsx           # Main app component
│   │   └── styles.css        # Global styles
│   ├── package.json          # Dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── .env.example          # Environment template
│   └── index.html            # HTML entry point
│
├── README.md                 # This file
├── VOICE_AND_ENV_SETUP.md   # Voice and environment setup guide
└── .gitignore               # Git ignore rules
```

## Prerequisites

- **Node.js** 16+ (for frontend)
- **Python** 3.9+ (for backend)
- **Microsoft SQL Server** (database)
- **Ollama** (for AI chat) - [Install Ollama](https://ollama.ai)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ironore-crm.git
cd ironore-crm
```

### 2. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Copy environment template and configure:
```bash
cp .env.example .env
# Edit .env with your SQL Server and Ollama credentials
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the backend server:
```bash
python -m uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup

Navigate to the frontend directory in a new terminal:
```bash
cd frontend
```

Copy environment template:
```bash
cp .env.example .env
# .env should have: VITE_API_BASE_URL=http://localhost:8000
```

Install dependencies:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Database Setup

### Create Tables
Run the SQL scripts in the `database/` folder to create necessary tables:

```bash
# Connect to your SQL Server and execute:
# database/add_complaint_columns.sql
# database/seed_inventory_data.sql
```

Or use the provided Python scripts:

```bash
# From backend directory:
python scripts/populate_inventory_data.py
```

## Configuration

### Environment Variables

#### Backend (.env)
- `MSSQL_SERVER`: SQL Server host
- `MSSQL_USER`: Database username
- `MSSQL_PASSWORD`: Database password
- `COMPANY_SUPPORT_EMAIL`: Support email for customer contact
- `COMPANY_SUPPORT_PHONE`: Support phone number
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `JWT_SECRET`: Secret key for JWT tokens

#### Frontend (.env)
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login

### Customer
- `GET /api/customer/me` - Get current customer info

### Chat
- `POST /api/chat` - Send chat message

### Products
- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product details
- `GET /api/categories` - List categories

### Specifications
- `GET /api/specs/iron-ore` - Get iron ore specs
- `GET /api/specs/iron-pellet` - Get iron pellet specs

### Complaints
- `POST /api/complaints` - Create complaint
- `GET /api/complaints` - List complaints

## Features in Detail

### Chat Assistant
- **Product Information**: Search for products and specifications
- **Order Placement**: Browse available products, place orders with quantity validation
- **Complaint Management**: Raise complaints, track status
- **Customer Support**: Direct contact with company

### Inventory Management
- **Real-time Availability**: Products shown only if stock is available
- **Automatic Deduction**: Orders automatically deduct from inventory
- **Stock Tracking**: Produced vs. Sold entries for complete audit trail

### Complaint Workflow
1. Customer raises complaint → Status: "Under Review"
2. Investigation starts → Root cause analysis, corrective actions
3. All data filled → Status: "Will be resolved in 2-3 working days"
4. Solution generated → Status: "Resolved"

## Development Scripts

Located in `backend/scripts/`:

- `populate_inventory_data.py` - Populate sample inventory data
- `check_inventory_schema.py` - Verify inventory table structure
- `populate_complaint.py` - Add test complaints
- `test_ollama_direct.py` - Test AI integration

Run scripts from backend directory:
```bash
python scripts/populate_inventory_data.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

### Backend Issues

**"Database connection failed"**
- Check SQL Server is running
- Verify credentials in `.env`
- Ensure database exists

**"Ollama connection failed"**
- Install Ollama: https://ollama.ai
- Start Ollama service: `ollama serve`
- Verify `OLLAMA_BASE_URL` in `.env`

### Frontend Issues

**"Cannot connect to API"**
- Ensure backend is running on port 8000
- Check `VITE_API_BASE_URL` in `.env`
- Clear browser cache

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Contact support at the email configured in `.env`

## Changelog

### Version 1.0.0
- Initial release
- AI-powered chat assistant
- Product and inventory management
- Complaint tracking system
- Order processing with inventory deduction
- Email contact feature
