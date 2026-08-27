# Iron Ore CRM - Floating Chat Button Test Documentation

## Overview

This document outlines comprehensive test coverage for the simplified Iron Ore CRM frontend that implements a **floating chat button interface** with AI-powered customer support capabilities. The system provides an omnichannel chat experience with quotation management, order placement, complaint tracking, and product information retrieval.

**Test Date:** August 27, 2026  
**Version:** 1.0  
**Application Scope:** Frontend Chat Widget + Backend Chat API

---

## 1. System Architecture

### Frontend Components
- **ChatWidget.jsx** - Main floating button and chat window interface
- **App.jsx** - Application entry point and authentication layer
- **api.js** - Backend API client with session management
- **styles.css** - Theme and UI styling (dark mode, animations)

### Backend Components
- **routers/chat.py** - Chat endpoint with AI intent classification
- **schemas.py** - Pydantic models for request/response validation
- **models.py** - SQLAlchemy database models
- **ollama_client.py** - LLM integration for conversational AI
- **auth.py** - JWT-based authentication

### Database Tables
- `Login_Master` - User authentication
- `Customer_Detail` - Customer information
- `Product_Master` - Product catalog
- `Inventory_Master` - Stock tracking (Produced/Sold in MT)
- `Complaints_Master` - Complaint lifecycle management
- `Quotations_Master` - Quote generation and tracking

---

## 2. Test Environment Setup

### Prerequisites
- **Browser:** Chrome 90+, Edge 90+, Safari 14+ (requires Web Speech API support)
- **Backend:** Python 3.9+, FastAPI running on `http://localhost:8000`
- **Database:** MSSQL Server with Customer_DB database
- **Environment Variables:**
  - `VITE_API_BASE_URL=http://localhost:8000`
  - Backend `.env` configured with database credentials

### Test Data Setup

```sql
-- Seed test customer
INSERT INTO Customer_Detail (CID, CustomerCode, CustomerName, ContactPerson, Email, Mobile, GSTNo, PANNo, Status)
VALUES ('CUST001', 'C001', 'Test Company Ltd', 'John Doe', 'john@test.com', '+919876543210', '27AABCT1234A1Z0', 'AAAPA1234A', 1)

-- Seed test products
INSERT INTO Product_Master (PID, ProductName, ProductCategory, PStatus)
VALUES 
  ('P001', 'Iron Ore Grade A', 1, 1),
  ('P002', 'Iron Ore Grade B', 1, 1),
  ('P003', 'Iron Pellets Standard', 2, 1)

-- Seed test inventory
INSERT INTO Inventory_Master (InventoryID, PID, Category, QuantityMT, ProducedDate, InitialPrice, SellingPrice)
VALUES 
  (1, 'P001', 'Produced', 1000.00, '2026-08-20', 4500, 5000),
  (2, 'P001', 'Sold', 500.00, '2026-08-21', 4500, 5000)
```

---

## 3. Functional Test Cases

### 3.1 Authentication & Session Management

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-001** | Valid Login | UserID: testuser, Password: testpass123 | JWT token issued, session stored in sessionStorage | ⏳ |
| **TC-002** | Invalid Credentials | UserID: testuser, Password: wrongpass | Error message: "Invalid user ID or password" | ⏳ |
| **TC-003** | Session Persistence | Close and reopen browser tab | User remains logged in (session restored) | ⏳ |
| **TC-004** | Session Expiration | Token expired in browser storage | User redirected to login or session refreshed | ⏳ |
| **TC-005** | Logout | Click logout button | Session cleared, redirected to login page | ⏳ |

### 3.2 Floating Chat Button Display

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-010** | Button Visibility | Page load with authenticated user | Orange circular "Fe" button visible at bottom-right | ⏳ |
| **TC-011** | Button Position | Resize browser window | Button remains in fixed position (bottom-right, 24px margin) | ⏳ |
| **TC-012** | Button Hover Effect | Hover mouse over button | Button scales up by 1.06x (smooth transition) | ⏳ |
| **TC-013** | Button Click - Open Chat | Click floating button | Chat window opens with welcome message | ⏳ |
| **TC-014** | Button Click - Close Chat | Click button again while chat open | Chat window closes, welcome message resets on reopen | ⏳ |
| **TC-015** | Mobile View | View on 320px mobile device | Button scales appropriately, stays visible | ⏳ |

### 3.3 Chat Window Interface

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-020** | Window Opening Animation | Click open button | Chat window slides up from bottom with shadow effect | ⏳ |
| **TC-021** | Welcome Message | Open chat | Personalized greeting: "Hello [CustomerName], I'm your CRM assistant..." | ⏳ |
| **TC-022** | Chat Header | Open chat | Header shows "CRM Assistant" title and "Clear chat" button | ⏳ |
| **TC-023** | Quick Action Buttons | Open chat | 5 action chips visible: Ask for Quotation, Place Order, Product Info, Raise Complaint, Connect to Company | ⏳ |
| **TC-024** | Close Button (X) | Chat window open | X button in header closes window | ⏳ |
| **TC-025** | Clear Chat Button | Send multiple messages | "Clear chat" button removes all messages, shows welcome again | ⏳ |
| **TC-026** | Message Scrolling | Send 10+ messages | Chat area auto-scrolls to latest message | ⏳ |
| **TC-027** | Responsive Height | Mobile vs desktop | Desktop: 612px height, Mobile: 70vh height | ⏳ |

### 3.4 Message Sending & Receiving

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-030** | Text Message Send | Type "What are your products?" → Click Send | Message appears in user bubble (orange), bot responds | ⏳ |
| **TC-031** | Enter Key Send | Type message → Press Enter | Message sent (Shift+Enter for newline) | ⏳ |
| **TC-032** | Empty Message | Click Send with no text | No message sent, button disabled | ⏳ |
| **TC-033** | Long Message | Textarea expands up to 90px | Message displays in full, wraps properly | ⏳ |
| **TC-034** | Message Loading State | Send message | Typing animation appears (3 bouncing dots) while waiting for response | ⏳ |
| **TC-035** | Network Error | Backend unavailable | Error message: "I'm unable to connect to the CRM service right now..." | ⏳ |
| **TC-036** | Error Message Display | Backend returns error | Error message displays in red bubble with warning styling | ⏳ |

### 3.5 Quick Action Buttons

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-040** | Ask for Quotation | Click "Ask for a Quotation" | Bot responds with available products list | ⏳ |
| **TC-041** | Place an Order | Click "Place an Order" | Bot shows order form with product selection | ⏳ |
| **TC-042** | Product Information | Click "Product Information" | Bot lists all active products with descriptions | ⏳ |
| **TC-043** | Raise a Complaint | Click "Raise a Complaint" | Bot shows complaint category selection | ⏳ |
| **TC-044** | Connect to Company | Click "Connect to Company" | Bot displays company email and contact details | ⏳ |
| **TC-045** | Button Disabled While Loading | Sending message | Quick action buttons disabled (opacity 0.5, no-click) | ⏳ |

### 3.6 Voice Input (Speech Recognition)

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-050** | Mic Button Display | Open chat | Microphone button visible in input area (🎙️ icon) | ⏳ |
| **TC-051** | Start Voice Input | Click mic button | Button changes to 🎤, listening indicator shows red pulse animation | ⏳ |
| **TC-052** | Voice to Text | Speak "Show me products" | Text recognized and populated in textarea | ⏳ |
| **TC-053** | Number Conversion | Speak "fifty" in quantity field | Converted to "50" | ⏳ |
| **TC-054** | Stop Listening | Click mic again while listening | Microphone stops, button returns to 🎙️ | ⏳ |
| **TC-055** | Unsupported Browser | Open in Firefox | Graceful message: "Speech recognition not supported..." | ⏳ |
| **TC-056** | Permission Denied | Deny microphone access | Error: "Microphone access denied. Please allow in browser settings" | ⏳ |
| **TC-057** | No Speech Detected | Click mic, stay silent for 10s | Error: "I didn't hear you. Please speak clearly..." | ⏳ |

### 3.7 Quotation Request Flow

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-060** | Show Available Products | Click "Ask for a Quotation" | List products with available stock (Produced - Sold) | ⏳ |
| **TC-061** | Select Product | Click product button | Form appears to enter quantity | ⏳ |
| **TC-062** | Enter Quantity | Type "100" in quantity field | Value accepted and validated | ⏳ |
| **TC-063** | Quantity Validation | Enter "500" but only 200 MT available | Error: "Only 200 MT available, but you requested 500 MT" | ⏳ |
| **TC-064** | Generate Quotation | Enter valid quantity → Click Submit | Quotation ID generated, PDF created, displayed in chat | ⏳ |
| **TC-065** | Quotation Details | Quotation generated | Response shows: Product name, Quantity, Price/MT, Total amount, Validity | ⏳ |
| **TC-066** | Quotation in Database | After generation | Record in Quotations_Master with status="Generated" | ⏳ |

### 3.8 Order Placement Flow

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-070** | Show Available Products | Click "Place an Order" | List products with available stock | ⏳ |
| **TC-071** | Select Product | Click product button | Order form displays | ⏳ |
| **TC-072** | Enter Quantity | Type "50" | Value accepted | ⏳ |
| **TC-073** | Submit Order | Enter quantity → Click Submit | Confirmation message with order details | ⏳ |
| **TC-074** | Insufficient Stock | Request more than available | Offer alternative: "Would you like to order [available qty] instead?" | ⏳ |

### 3.9 Complaint Management

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-080** | Complaint Categories | Click "Raise a Complaint" | Show available categories (Quality, Delivery, Billing, etc.) | ⏳ |
| **TC-081** | Select Category | Click "Quality" | Category selected, form shows for detailed info | ⏳ |
| **TC-082** | Enter Complaint Details | Fill category, description, PO number, dispatch date | All fields accept input without errors | ⏳ |
| **TC-083** | Submit Complaint | Fill form → Click Submit | Complaint saved, tracking ID returned (e.g., CPLNT-20260827-001) | ⏳ |
| **TC-084** | Complaint Confirmation | After submission | Message: "Your complaint has been registered with tracking number [ID]" | ⏳ |
| **TC-085** | Track Complaint | Click "Track my Complaint" → Enter complaint ID | Show complaint status (Open, In Progress, Resolved) | ⏳ |
| **TC-086** | Complaint in Database | After submission | Record created in Complaints_Master with CreatedDate, Status, etc. | ⏳ |

### 3.10 Product Information Queries

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-090** | List All Products | Type "What products do you have?" | Bot lists all active products with categories | ⏳ |
| **TC-091** | Product Specifications | Type "Fe specification for P001" | Show Iron Ore specs: Parameter → Specification pairs | ⏳ |
| **TC-092** | Pellet Specifications | Type "Pellet specs" | Show Iron Pellet specs with Testing Standards | ⏳ |
| **TC-093** | Inventory Status | Type "What's the stock for P002?" | Show available quantity: Produced - Sold | ⏳ |
| **TC-094** | Customer Information | Type "Show my details" | Display: Company name, contact person, email, address, GST/PAN | ⏳ |

### 3.11 AI Intent Classification

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-100** | Quotation Intent | "I need a price quote for Iron Ore" | Intent classified as QUOTATION_REQUEST | ⏳ |
| **TC-101** | Complaint Intent | "Your product quality is poor" | Intent classified as COMPLAINT | ⏳ |
| **TC-102** | Product Intent | "Tell me about your products" | Intent classified as PRODUCT_INFORMATION | ⏳ |
| **TC-103** | Specification Intent | "What are the specifications?" | Intent classified as IRON_ORE_SPECIFICATION or IRON_PELLET_SPECIFICATION | ⏳ |
| **TC-104** | Ambiguous Intent | "Hello" | Bot requests clarification with quick action buttons | ⏳ |

### 3.12 Data Security & Validation

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-110** | SQL Injection Prevention | Type "'; DROP TABLE--" | Message sanitized, displayed as-is (no injection) | ⏳ |
| **TC-111** | XSS Prevention | Type "<script>alert('XSS')</script>" | Script escaped, displayed as text | ⏳ |
| **TC-112** | Credential Redaction | LLM outputs "password=abc123" | Response sanitized to "[redacted]" | ⏳ |
| **TC-113** | Customer CID Isolation | Customer A queries product | Customer B's CID not visible in response | ⏳ |
| **TC-114** | Authentication Required | Access chat without login | Chat button not available, redirected to login | ⏳ |

### 3.13 Error Handling

| Test ID | Test Case | Input | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| **TC-120** | Network Timeout | Backend slow response (5+ sec) | Timeout error displayed gracefully | ⏳ |
| **TC-121** | Invalid JSON Response | Backend returns malformed JSON | Error: "Unable to process response" | ⏳ |
| **TC-122** | Database Connection Error | Database unavailable | Error: "Service unavailable, please try again" | ⏳ |
| **TC-123** | Missing Required Fields | Complaint form missing description | Validation error: "Description is required" | ⏳ |
| **TC-124** | Expired Token | Token expired during chat | Auto-logout or token refresh attempt | ⏳ |

---

## 4. UI/UX Test Cases

| Test ID | Test Case | Expected Result | Status |
|---------|-----------|-----------------|--------|
| **TC-130** | Dark Theme Consistency | All UI elements follow dark color scheme (--bg, --surface, --accent-ore) | ⏳ |
| **TC-131** | Typography Readability | Font sizes, line-height, and color contrast WCAG AA compliant | ⏳ |
| **TC-132** | Button Accessibility | All buttons have proper aria-labels and keyboard focus | ⏳ |
| **TC-133** | Message Alignment | User messages right-aligned (orange), bot left-aligned (gray) | ⏳ |
| **TC-134** | Avatar Display | User has avatar "U", bot has avatar "Fe" | ⏳ |
| **TC-135** | Loading Animation | Typing bubble with 3 dots, smooth animation | ⏳ |
| **TC-136** | Color Contrast | Text readable on all backgrounds (accessibility) | ⏳ |
| **TC-137** | Mobile Responsiveness | Chat scales from 320px to 1920px without overflow | ⏳ |

---

## 5. Performance Test Cases

| Test ID | Test Case | Acceptance Criteria | Status |
|---------|-----------|-------------------|--------|
| **TC-140** | Chat Window Load Time | <2 seconds to open | ⏳ |
| **TC-141** | Message Send Response | <3 seconds for LLM response | ⏳ |
| **TC-142** | Quotation Generation | <5 seconds to generate PDF | ⏳ |
| **TC-143** | Page Load (Authenticated) | <2 seconds to display chat button | ⏳ |
| **TC-144** | Memory Usage | No memory leaks after 100+ messages | ⏳ |
| **TC-145** | Concurrent Requests | Handle 10 simultaneous chat requests | ⏳ |

---

## 6. Regression Test Suite

These tests ensure core functionality remains stable:

### Critical Path (Must Pass)
- TC-001: Valid Login
- TC-013: Button Click - Open Chat
- TC-030: Text Message Send
- TC-040: Ask for Quotation (full flow)
- TC-080: Raise Complaint (full flow)
- TC-090: Product Information Query

### Integration Tests
- TC-060 → TC-066: Full quotation workflow
- TC-070 → TC-074: Full order workflow
- TC-080 → TC-086: Full complaint workflow

---

## 7. Browser & Device Testing Matrix

| Browser | Version | Desktop | Mobile | Status |
|---------|---------|---------|--------|--------|
| Chrome | 90+ | ✓ | ✓ | ⏳ |
| Edge | 90+ | ✓ | ✓ | ⏳ |
| Safari | 14+ | ✓ | ✓ | ⏳ |
| Firefox | 88+ | ✓ | ⚠️ (limited speech) | ⏳ |

**Note:** Firefox does not support Web Speech API natively (speech recognition unavailable).

---

## 8. Test Execution Checklist

- [ ] All TC-001 to TC-005 (Authentication) passed
- [ ] All TC-010 to TC-027 (Chat UI) passed
- [ ] All TC-030 to TC-036 (Messaging) passed
- [ ] All TC-040 to TC-045 (Quick Actions) passed
- [ ] All TC-050 to TC-057 (Voice Input) passed
- [ ] All TC-060 to TC-066 (Quotation) passed
- [ ] All TC-070 to TC-074 (Orders) passed
- [ ] All TC-080 to TC-086 (Complaints) passed
- [ ] All TC-090 to TC-094 (Product Info) passed
- [ ] All TC-100 to TC-104 (AI Intent) passed
- [ ] All TC-110 to TC-114 (Security) passed
- [ ] All TC-120 to TC-124 (Error Handling) passed
- [ ] All TC-130 to TC-137 (UI/UX) passed
- [ ] All TC-140 to TC-145 (Performance) passed
- [ ] Browser matrix testing completed
- [ ] Regression tests passed

---

## 9. Known Issues & Limitations

### Current Limitations
1. **No multi-tab synchronization** - Chat state not synced across browser tabs
2. **Session timeout** - No automatic token refresh (manual login required after expiry)
3. **File uploads** - Not supported in chat (text/voice only)
4. **Chat history** - Not persisted to database (reset on page reload)
5. **PDF download** - Quotations generated but download not explicitly tested

### Known Issues
- Speech recognition may fail if microphone blocked at OS level
- Large messages (>5000 chars) may cause rendering delays
- Rapid message sending can cause race conditions in UI state

---

## 10. Test Reports & Metrics

### Sample Test Report Template

```
Test Run: [Date]
Tester: [Name]
Environment: [Chrome v115, Windows 11, localhost]

Total Tests: 145
Passed: ___
Failed: ___
Blocked: ___
Skipped: ___

Pass Rate: ____%
Critical Issues: ___
Major Issues: ___
Minor Issues: ___

Notes:
- [Issue description]
- [Blocker description]
```

---

## 11. API Endpoint Testing

### POST /api/chat
**Request:**
```json
{
  "message": "Show me available products",
  "action": null
}
```

**Response Success (200):**
```json
{
  "reply": "Here are our available products: Iron Ore Grade A, Iron Ore Grade B, Iron Pellets Standard",
  "data": {
    "products": [
      {"PID": "P001", "name": "Iron Ore Grade A"},
      {"PID": "P002", "name": "Iron Ore Grade B"},
      {"PID": "P003", "name": "Iron Pellets Standard"}
    ]
  }
}
```

**Response Error (400):**
```json
{
  "detail": "Invalid request format"
}
```

### POST /api/complaints
**Request:**
```json
{
  "category_type": "Quality",
  "description": "Product quality below standard",
  "po_number": "PO-2026-001",
  "dispatch_date": "2026-08-25"
}
```

**Response Success (201):**
```json
{
  "ComplaintID": "CPLNT-20260827-001",
  "Status": "Open",
  "CreatedDate": "2026-08-27T14:30:00"
}
```

---

## 12. Conclusion

This test documentation provides comprehensive coverage for the Iron Ore CRM floating chat button interface. All test cases should be executed before production deployment. The focus is on:

1. ✅ Chat functionality and UI responsiveness
2. ✅ AI intent classification accuracy
3. ✅ Business workflow completeness (quotations, orders, complaints)
4. ✅ Security and data isolation
5. ✅ Error handling and graceful degradation
6. ✅ Performance and load handling

**Next Steps:**
- Execute full test suite
- Document any failures with screenshots
- Performance benchmark on target environment
- Accessibility audit (WCAG 2.1 AA)
- Security penetration testing
- User acceptance testing (UAT)

---

**Document Version:** 1.0  
**Last Updated:** August 27, 2026  
**Status:** Ready for Testing  
**Owner:** QA Team
