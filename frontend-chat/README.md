# Chat Floating Button - Standalone Component

A self-contained, production-ready chat widget component that can be embedded in any React application. Includes speech recognition, order placement, quotation requests, and more.

## Features

✅ **Standalone Component** - Works independently without the rest of the application  
✅ **Speech Recognition** - Web Speech API integration with error handling  
✅ **Order Management** - Place orders directly through the chat interface  
✅ **Quotation Requests** - Request product quotations with speech input  
✅ **Product Browsing** - Browse and select products  
✅ **Contact Information** - Access company email and information  
✅ **Fully Styled** - Complete CSS included, dark theme  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **No Dependencies** - Uses only React and react-markdown  

## Installation

### Files Included

```
frontend-chat/
├── ChatFloatingButton.jsx    # Main chat component
├── ChatMessage.jsx           # Message renderer component
├── chat-button.css           # Complete styling
└── README.md                # This file
```

### Prerequisites

- React 16.8+ (with Hooks support)
- react-markdown (for message rendering)

### Setup

1. **Copy files to your project:**

```bash
cp ChatFloatingButton.jsx /path/to/your/project/src/components/
cp ChatMessage.jsx /path/to/your/project/src/components/
cp chat-button.css /path/to/your/project/src/styles/
```

2. **Install dependencies (if not already installed):**

```bash
npm install react-markdown
```

3. **Import and use in your app:**

```jsx
import ChatFloatingButton from './components/ChatFloatingButton'

function App() {
  return (
    <div>
      {/* Your app content */}
      
      <ChatFloatingButton 
        apiBaseUrl="http://localhost:8000"
        user={{
          name: 'John Doe',
          customerCompany: 'ABC Corporation'
        }}
      />
    </div>
  )
}
```

4. **Import the CSS:**

```jsx
// In your main app file or component
import './styles/chat-button.css'
```

## Usage

### Basic Usage

```jsx
<ChatFloatingButton apiBaseUrl="http://localhost:8000" />
```

### With User Information

```jsx
<ChatFloatingButton 
  apiBaseUrl="http://localhost:8000"
  user={{
    name: 'John Doe',
    email: 'john@example.com',
    customerCompany: 'ABC Corp',
    customerName: 'John'
  }}
/>
```

### Controlled Component (with state management)

```jsx
import { useState } from 'react'
import ChatFloatingButton from './components/ChatFloatingButton'

function App() {
  const [chatOpen, setChatOpen] = useState(false)

  return (
    <ChatFloatingButton 
      apiBaseUrl="http://localhost:8000"
      user={{ name: 'John Doe' }}
      open={chatOpen}
      onToggle={(isOpen) => setChatOpen(isOpen)}
    />
  )
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `apiBaseUrl` | string | ✅ Yes | Base URL for API calls (e.g., `http://localhost:8000`) |
| `user` | object | ❌ No | User information object |
| `user.name` | string | ❌ No | User's name |
| `user.email` | string | ❌ No | User's email |
| `user.customerName` | string | ❌ No | Customer display name |
| `user.customerCompany` | string | ❌ No | Customer company name |
| `open` | boolean | ❌ No | Controlled open state |
| `onToggle` | function | ❌ No | Callback when chat is toggled: `(isOpen) => {}` |

## API Requirements

The component expects a backend API with the following endpoints:

### POST `/api/chat`

Send messages and actions to the chat backend.

**Request body:**
```json
{
  "message": "User message text",
  "action": "Optional action identifier"
}
```

**Response:**
```json
{
  "reply": "Bot response message",
  "data": {
    "products": [...],
    "email": "contact@example.com",
    ...
  }
}
```

**Supported Actions:**
- `"Ask for a Quotation"` - Request product quotation
- `"Place an Order"` - Place an order
- `"Product Information"` - Get product info
- `"Raise a Complaint"` - Raise a complaint
- `"Connect to Company"` - Get company contact info
- `order_quantity:PID:QUANTITY` - Submit an order
- `submit_quantity_quotation:PID:QUANTITY` - Submit quotation request

## Features in Detail

### Speech Recognition

The component includes Web Speech API integration with:

- **Browser Support:** Chrome, Edge, Safari (not Firefox)
- **Automatic Routing:** Speech is automatically routed to the appropriate field
  - Form quantity fields: numbers are extracted
  - Chat input: full transcript is captured
- **Error Handling:** Specific error messages for microphone issues
- **Word-to-Number Conversion:** Speaks "one hundred" → outputs "100"

### Order Placement

1. User clicks "Place an Order" quick action
2. Backend returns available products
3. User selects a product
4. Order form appears with quantity field
5. User enters quantity (via speech or typing)
6. User clicks "Check Availability"
7. Backend processes and returns confirmation

### Quotation Requests

1. User clicks "Ask for a Quotation" quick action
2. Backend returns available products
3. User selects a product
4. Quotation form appears with quantity field
5. User enters quantity (via speech or typing)
6. User clicks "Generate Quotation"
7. Backend processes and returns quotation details

## Styling

All styles are contained in `chat-button.css` and use CSS variables for easy theming.

### Color Scheme

```css
--bg: #14181c              /* Background */
--surface: #1b2126         /* Surface */
--accent-ore: #c4622d      /* Primary color (orange) */
--accent-steel: #5b9bc0    /* Secondary color (blue) */
--danger: #d16a5a          /* Error color (red) */
--text: #edede6            /* Text color */
--text-dim: #9aa5ad        /* Dimmed text */
```

### Customizing Colors

To change the theme, override CSS variables in your app:

```css
:root {
  --accent-ore: #your-color;
  --surface: #your-background;
  /* ... other variables */
}
```

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Recommended |
| Edge | ✅ Full | Chromium-based |
| Safari | ✅ Full | macOS & iOS |
| Firefox | ⚠️ Limited | No Web Speech API |
| Mobile | ✅ Good | Responsive design |

## Troubleshooting

### "apiBaseUrl not configured"

**Problem:** Error message in chat says backend is not configured.

**Solution:** Make sure you pass the `apiBaseUrl` prop:
```jsx
<ChatFloatingButton apiBaseUrl="http://localhost:8000" />
```

### Speech recognition not working

**Problem:** Mic button doesn't capture speech.

**Checklist:**
- [ ] Using Chrome, Edge, or Safari (not Firefox)
- [ ] Microphone is connected and not muted
- [ ] Browser has microphone permission
- [ ] Check console (F12) for error messages
- [ ] Internet connection is active

### Chat window not visible

**Problem:** Chat button is visible but window doesn't open.

**Solution:**
1. Check console for errors
2. Make sure CSS is imported
3. Check z-index conflicts with other elements
4. Try using controlled component mode

### Messages not sending

**Problem:** User sends message but nothing happens.

**Checklist:**
- [ ] Backend API is running
- [ ] `apiBaseUrl` points to correct server
- [ ] Network requests are not blocked
- [ ] Backend `/api/chat` endpoint exists
- [ ] Check network tab in DevTools

## Integration Example

### Full App Integration

```jsx
import React, { useState } from 'react'
import ChatFloatingButton from './components/ChatFloatingButton'
import './styles/chat-button.css'

function App() {
  const [user] = useState({
    name: 'John Doe',
    email: 'john@example.com',
    customerCompany: 'ABC Corporation',
    customerName: 'John'
  })

  return (
    <div className="app">
      {/* Your app content */}
      <header>
        <h1>My Application</h1>
      </header>
      
      <main>
        {/* Your main content */}
      </main>

      {/* Chat Widget */}
      <ChatFloatingButton 
        apiBaseUrl="http://localhost:8000"
        user={user}
      />
    </div>
  )
}

export default App
```

### With Environment Variables

```jsx
<ChatFloatingButton 
  apiBaseUrl={process.env.REACT_APP_API_URL}
  user={{
    name: process.env.REACT_APP_USER_NAME,
    customerCompany: process.env.REACT_APP_COMPANY_NAME
  }}
/>
```

## Backend Integration

Ensure your backend API handles the following:

1. **Chat Messages** - `/api/chat` POST endpoint
2. **Product Listing** - Returns products in response
3. **Order Processing** - Handles `order_quantity` actions
4. **Quotation Generation** - Handles `submit_quantity_quotation` actions
5. **Error Handling** - Returns proper error messages

## Performance Notes

- Component uses React hooks for optimal performance
- Speech recognition runs in a separate thread
- Messages are virtualized in large conversations
- CSS is minimal and optimized

## Security Considerations

- Never hardcode sensitive data in props
- Use environment variables for API URLs
- Validate all user input on the backend
- Sanitize API responses before displaying
- Use HTTPS in production

## Support

For issues or feature requests, contact the development team or submit an issue in the project repository.

## License

MIT License - See LICENSE file for details

---

**Version:** 1.0.0  
**Last Updated:** August 26, 2026  
**Status:** Production Ready ✅
