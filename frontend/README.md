# Iron Ore CRM - Frontend

React + Vite frontend for the Iron Ore CRM system with real-time AI chat, quotation generation, complaint tracking, and order management.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/               # Reusable React components
│   │   ├── ChatWidget.jsx        # Main chat interface
│   │   ├── ChatMessage.jsx       # Individual message display
│   │   ├── ProductCard.jsx       # Product display card
│   │   └── __pycache__/          # Component cache
│   ├── pages/                    # Page components
│   │   ├── Login.jsx             # User login page
│   │   ├── Dashboard.jsx         # Main dashboard
│   │   └── (routed pages)
│   ├── App.jsx                   # Root component
│   ├── api.js                    # API client & utilities
│   ├── main.jsx                  # Vite entry point
│   ├── styles.css                # Global styles
│   └── (other assets)
├── public/                       # Static assets
├── index.html                    # HTML template
├── vite.config.js               # Vite configuration
├── package.json                 # npm dependencies
├── package-lock.json            # Dependency lock file
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ & npm
- Modern web browser
- Backend API running on http://localhost:8000

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd ironore-crm/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with API endpoint
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

The app will be available at `http://localhost:5173`

---

## 📝 Environment Variables (`.env`)

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api

# Frontend Settings
VITE_APP_NAME=Iron Ore CRM
VITE_CHAT_ENABLED=true
```

---

## 🎯 Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter (if configured)
npm run lint
```

---

## 🧩 Key Components

### ChatWidget (`components/ChatWidget.jsx`)
Main chat interface component handling:
- Message sending and receiving
- State management for chat, complaints, orders, quotations
- Voice input with Web Speech API
- Intent-based action handling
- Real-time message display

**Props:**
- `user` - Logged-in user object
- `open` - Chat widget visibility
- `onToggle` - Toggle chat function
- `pendingAction` - Queued user action

**Features:**
- ✅ Text input with auto-resize
- ✅ Voice input/output support
- ✅ Complaint workflow
- ✅ Order placement
- ✅ Quotation generation
- ✅ Product information
- ✅ Email contact

### ChatMessage (`components/ChatMessage.jsx`)
Individual message display component with:
- Markdown rendering
- Interactive complaint ID buttons
- Product selection buttons
- Quantity input forms
- Email contact display

**Props:**
- `role` - "user" or "bot"
- `text` - Message text
- `showComplaintCategories` - Show complaint options
- `showOrderProducts` - Show order product list
- `showQuotationProducts` - Show quotation product list
- `companyEmail` - Show company email contact

**Dynamic UI Elements:**
- Complaint category selection
- Complaint form with PO number and dispatch date
- Order product buttons
- Order quantity input
- Quotation product buttons
- Quotation quantity input
- Company email with mailto link

### ProductCard (`components/ProductCard.jsx`)
Product display component showing:
- Product name
- Product ID
- Availability status
- Action buttons

### Login (`pages/Login.jsx`)
Authentication page with:
- User ID input
- Password input
- Remember me checkbox
- Error handling
- Session management

### Dashboard (`pages/Dashboard.jsx`)
Main dashboard with:
- User greeting
- Chat widget
- Quick action buttons
- Navigation

---

## 🔄 User Workflows

### 1. Quotation Generation
```
Login → Dashboard → Click "Ask for a Quotation"
  ↓
See available products list
  ↓
Click product button
  ↓
Enter quantity (MT)
  ↓
Click "Generate Quotation"
  ↓
View quotation with PDF link
```

### 2. Order Placement
```
Click "Place an Order"
  ↓
See available products
  ↓
Click product
  ↓
Enter quantity
  ↓
Verify availability
  ↓
Order placed successfully
```

### 3. Raise Complaint
```
Click "Raise a Complaint"
  ↓
Select complaint category
  ↓
Enter PO number & dispatch date
  ↓
Describe issue
  ↓
Submit complaint
  ↓
Receive complaint ID
```

### 4. Contact Company
```
Click "Contact Company via Email"
  ↓
See company email address
  ↓
Click email button
  ↓
Mail client opens
  ↓
Send email
```

---

## 🎨 Styling

### Global Styles (`src/styles.css`)
CSS variables and themes:
```css
--primary-bg: #1a1a1a
--surface: #2a2a2a
--accent-ore: #c4622d
--text: #ffffff
--text-dim: #999999
--border: #404040
```

### Component Styling
- Inline styles for dynamic behavior
- Hover effects and transitions
- Responsive layout
- Accessibility support

---

## 🔐 Authentication

### Login Flow
1. User enters credentials
2. Frontend sends to `/api/auth/login`
3. Backend returns JWT token
4. Token stored in state/session
5. Token included in API headers: `Authorization: Bearer <token>`

### Token Management
- Auto-refresh on page load
- Logout clears token
- Protected routes check token validity

---

## 💬 Chat System

### Supported Intents
- **GREETING** - Welcome message
- **PRODUCT_INFORMATION** - Product details
- **ORDER_REQUEST** - Place orders
- **QUOTATION_REQUEST** - Generate quotations
- **COMPLAINT** - Raise complaints
- **COMPLAINT_TRACKING** - Track complaints
- **WHATSAPP_CONTACT** - Company email

### Message Flow
```
User sends message/action
    ↓
ChatWidget.sendMessage()
    ↓
api.chat() → Backend
    ↓
Backend detects intent
    ↓
Returns response + structured data
    ↓
Frontend renders message + UI elements
    ↓
Display in ChatMessage component
```

---

## 🗣️ Voice Input

Uses Web Speech API for voice input:
```javascript
// Microphone button toggles listening
// Spoken text captured and sent as message
// Requires HTTPS (or localhost for development)
```

---

## 📱 API Integration

### API Client (`src/api.js`)

```javascript
// Initialize API client
import { api } from './api.js'

// Send chat message
const response = await api.chat(message, action)

// Response structure
{
  reply: "...",           // Text response
  intent: "...",          // Detected intent
  data: {...},            // Structured data (products, etc)
  suggested_actions: []   // Next action suggestions
}
```

### Error Handling
```javascript
try {
  const res = await api.chat(text, action)
} catch (err) {
  if (err instanceof ApiError) {
    // Handle API errors
  } else {
    // Handle network errors
  }
}
```

---

## 🚀 Building for Production

1. **Build the application:**
   ```bash
   npm run build
   ```
   Creates optimized build in `dist/` directory

2. **Deploy to server:**
   - Copy contents of `dist/` to web server
   - Configure backend API URL
   - Enable HTTPS
   - Set up reverse proxy if needed

3. **Environment configuration:**
   ```bash
   # Production .env
   VITE_API_BASE_URL=https://api.yourdomain.com
   ```

---

## 🧪 Testing

### Manual Testing
1. Login with test credentials
2. Test each quick action
3. Verify UI renders correctly
4. Check error messages
5. Test on different browsers

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 🐛 Troubleshooting

### Backend Connection Issues
```
Error: "Failed to connect to backend"
Solution:
1. Verify backend is running on localhost:8000
2. Check VITE_API_BASE_URL in .env
3. Check browser console for CORS errors
4. Verify API endpoint responds: http://localhost:8000/docs
```

### Chat Not Responding
```
Error: "Chat request timeout"
Solution:
1. Check backend server logs
2. Verify Ollama is running (for AI responses)
3. Check network connection
4. Try refreshing the page
```

### Login Issues
```
Error: "Invalid credentials"
Solution:
1. Verify user exists in database
2. Check password is correct
3. Verify backend authentication is working
4. Check browser console for token errors
```

### Voice Input Not Working
```
Error: "Microphone permission denied"
Solution:
1. Check browser microphone permissions
2. Allow microphone access when prompted
3. Use HTTPS (or localhost for dev)
4. Try different browser
5. Check if Ollama is enabled
```

---

## 📦 Dependencies

Key packages:
- **react** - UI library
- **react-markdown** - Markdown rendering
- **vite** - Build tool
- **axios** - HTTP client (via api.js)

See `package.json` for complete list.

---

## 🎯 Key Features

✅ **Real-time Chat**
- AI-powered responses
- Multiple intent support
- Intent classification

✅ **Quotation Generation**
- Product selection UI
- Quantity input
- PDF quotation download
- Price calculation

✅ **Order Management**
- Product availability check
- Order tracking
- Inventory integration

✅ **Complaint Handling**
- Multi-category support
- Status tracking
- Historical view
- Complaint ID search

✅ **Contact Options**
- Email with mailto link
- Phone display
- WhatsApp integration ready

✅ **Voice Input**
- Microphone support
- Transcription to text
- Accessibility feature

✅ **Responsive Design**
- Mobile-friendly
- Tablet support
- Desktop optimization

---

## 🔗 Related Documentation

- **Backend:** See `../backend/README.md`
- **Project Root:** See `../README.md`
- **Quotation Feature:** See `../backend/QUOTATION_FEATURE.md`

---

## 💡 Development Tips

### Adding New Chat Feature
1. Add intent to backend `app/intent.py`
2. Create handler in `app/routers/chat.py`
3. Add UI component in `ChatMessage.jsx`
4. Pass props through `ChatWidget.jsx`
5. Handle response rendering
6. Test end-to-end

### Styling Changes
1. Edit `src/styles.css` for global styles
2. Use inline styles for component-specific
3. Maintain CSS variable consistency
4. Test on multiple screen sizes

### Adding API Endpoint
1. Create endpoint in backend
2. Add to `src/api.js` client
3. Import in component
4. Call with error handling
5. Display response

---

## 📊 Performance Optimization

- Lazy loading for heavy components
- Memoization for expensive computations
- Message virtualization for long chats
- Code splitting with Vite
- CSS optimization in build

---

## ♿ Accessibility

- Semantic HTML structure
- ARIA labels where appropriate
- Keyboard navigation support
- Voice input for accessibility
- Color contrast compliance

---

## 📞 Support

For issues:
1. Check troubleshooting section
2. Review component props/states
3. Check browser console
4. Check backend logs
5. Contact: rshashidhar513@gmail.com

---

**Last Updated:** August 22, 2026
**Version:** 1.0.0
