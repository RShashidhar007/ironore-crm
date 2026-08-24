# Quotation Feature - Frontend Integration Guide

## Overview

The quotation generation feature is fully implemented on the backend. The frontend needs to handle the chat flow for quotation requests.

## User Journey

### 1. Action Button Click
User clicks "Ask for a Quotation" button → sends `action="Ask for a Quotation"` to chat API

### 2. Show Available Products
Backend returns available products list → display to user

Example Response:
```json
{
  "reply": "Hello [Customer], I can help you with a quotation.\n\n**Available Products:**\n• LOW CCS IRON ORE PELLET (ID: 13000000)...",
  "structured_data": {
    "available_products": [
      {"pid": "13000000", "name": "LOW CCS IRON ORE PELLET"},
      {"pid": "13000001", "name": "Unscreened Accretion"}
    ]
  }
}
```

### 3. User Selects Product & Quantity
User inputs:
- Product ID or name
- Quantity in MT
- Optional notes

Example: "13000000, 100 MT, FOB Port Chennai"

### 4. Generate Quotation
Frontend sends to chat endpoint with action format:
```
action: "generate_quotation:13000000:100:FOB Port Chennai"
```

### 5. Display Quotation
Backend returns quotation details with PDF link:

```json
{
  "reply": "QUOTATION GENERATED\n\nQuotation Number: QT-2026-08-001...",
  "action_buttons": ["Download PDF", "View Details", "Modify Quotation"],
  "structured_data": {
    "quotation_id": 1,
    "quotation_number": "QT-2026-08-001",
    "product_id": "13000000",
    "quantity_mt": 100.0,
    "price_per_mt": 5150.00,
    "total_amount": 515000.00,
    "pdf_path": "quotations/QT-2026-08-001_20260815_143022.pdf"
  }
}
```

## Implementation Steps

### Step 1: Update Chat Widget
Ensure "Ask for a Quotation" button sends correct action:

```jsx
// In ChatWidget.jsx or similar
const handleActionClick = (action) => {
  // This already exists
  sendMessage("", action);
};

// Ensure action buttons include:
const ALL_ACTIONS = [
  "Ask for a Quotation",     // ✓ Already exists
  "Place an Order",
  "Product Information",
  "Raise a Complaint",
  "Track my Complaint",
  "Contact Company via Email",
];
```

### Step 2: Handle Quotation Response Display
When `structured_data.quotation_number` is present, display:

```jsx
{
  // Show quotation summary
  quotation_number, 
  product_name,
  quantity_mt,
  price_per_mt,
  total_amount,
  expiry_date
}

// Add download button
if (structured_data.pdf_path) {
  <button onClick={() => downloadPDF(quotation_id)}>
    📥 Download PDF
  </button>
}
```

### Step 3: Collect Product & Quantity Input
After showing available products, collect user input:

```jsx
// Listen for next user message after product list
// Parse message to extract:
// - productId (or productName)
// - quantity
// - notes (optional)

// Format as action for backend:
const action = `generate_quotation:${productId}:${quantity}:${notes || ""}`;
sendMessage("", action);
```

### Step 4: Add PDF Download Handler
Create endpoint to download quotation PDF:

```jsx
const downloadPDF = async (quotationId) => {
  const response = await fetch(
    `/api/quotations/${quotationId}/pdf`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `quotation-${quotationId}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
};
```

## API Integration

### Generate Quotation
```
POST /api/chat
{
  "message": "",
  "action": "generate_quotation:13000000:100:Notes here"
}
```

Response includes:
- `reply`: Text quotation
- `structured_data`: Quotation details
- `action_buttons`: Next actions

### Download PDF
```
GET /api/quotations/{quotation_id}/pdf
Authorization: Bearer {token}
```

Returns: PDF file (application/pdf)

### Get Quotation Details
```
GET /api/quotations/{quotation_id}
Authorization: Bearer {token}
```

Returns: Quotation JSON with all details

### List Customer Quotations
```
GET /api/quotations
Authorization: Bearer {token}
```

Returns: Array of customer's quotations

## Chat Action Format

### Format
```
generate_quotation:PID:QUANTITY:NOTES
```

### Examples
```
generate_quotation:13000000:100:
generate_quotation:13000001:50:FOB Port Chennai
generate_quotation:13000002:200:Include inspection certificate
```

### Parsing in Frontend
```jsx
const extractQuotationData = (message) => {
  // Extract from user message like "13000000, 100 MT, FOB Port"
  // or "Product 13000000, quantity 100, FOB Port Chennai"
  
  const pidMatch = message.match(/13000\d{3}/);
  const qtyMatch = message.match(/(\d+(?:\.\d+)?)\s*MT/i);
  const notes = message
    .replace(pidMatch?.[0], '')
    .replace(qtyMatch?.[0], '')
    .trim();
  
  return {
    productId: pidMatch?.[0],
    quantity: qtyMatch?.[1],
    notes: notes
  };
};
```

## Response Handling

### Quotation Generated Successfully
```json
{
  "reply": "QUOTATION GENERATED...",
  "action_buttons": ["Download PDF", "View Details", "Modify Quotation"],
  "structured_data": {
    "quotation_id": 1,
    "quotation_number": "QT-2026-08-001",
    ...
  }
}
```

Display:
- ✅ Show quotation details card
- 📄 Show PDF download button
- 💾 Save quotation_id for later reference
- 📧 Option to email quotation

### Error Cases

**Product not found:**
```
"Product 13000 not found. Please check the product ID..."
```

**Invalid quantity:**
```
"Invalid quantity format. Please provide a valid number."
```

**No products available:**
```
"I apologize but we don't have any products available for quotation..."
```

## UI Components Needed

### 1. Product Selection Component
- Show list of available products
- Allow search/filter by product name or ID
- Display product category and availability

### 2. Quantity Input
- Number input field
- Validate: quantity > 0
- Display available quantity (optional)
- Unit: MT (Metric Tons)

### 3. Quotation Display Card
```
┌─────────────────────────────────┐
│ QUOTATION GENERATED             │
├─────────────────────────────────┤
│ QT-2026-08-001                  │
│ Product: LOW CCS IRON ORE...    │
│ Quantity: 100.00 MT             │
│ Price: ₹ 5,150.00/MT           │
│ Total: ₹ 515,000.00            │
│ Valid Till: 2026-08-22         │
├─────────────────────────────────┤
│ [📥 Download PDF] [📋 Details] │
└─────────────────────────────────┘
```

### 4. Price History Display (Optional)
```
Recent Pricing:
• 15-08-2026: ₹ 5,200.00/MT
• 08-08-2026: ₹ 5,150.00/MT
• 01-08-2026: ₹ 5,100.00/MT
Average: ₹ 5,150.00/MT
```

## Testing Checklist

- [ ] Action button "Ask for a Quotation" displays products
- [ ] User can enter product ID and quantity
- [ ] Quotation is generated correctly
- [ ] PDF download link works
- [ ] Quotation number is displayed
- [ ] Price history is shown
- [ ] Expiry date is calculated correctly (7 days)
- [ ] Multiple quotations can be created
- [ ] User can view previous quotations
- [ ] Error messages display for invalid input

## Troubleshooting

### PDF Download Not Working
- Check if quotation has PDFFilePath
- Verify PDF file exists at path
- Check CORS headers allow file download
- Test `/api/quotations/{id}/pdf` directly

### Quotation Generation Fails
- Verify product exists in database
- Check quantity is > 0
- Ensure customer CID is set
- Check database connection

### Products Not Showing
- Verify inventory has "Produced" entries
- Check QuantityMT > 0 for Produced items
- Filter: Produced quantity - Sold quantity > 0

## Future Enhancements

- [ ] Multi-product quotations (basket)
- [ ] Volume-based discounts
- [ ] Quotation templates/presets
- [ ] Email quotation directly
- [ ] Quotation comparison
- [ ] Approval workflow
- [ ] Automatic order conversion
- [ ] Quotation expiry notifications

---

**Integration Status:** ✅ Backend Complete, Frontend Integration Needed  
**Last Updated:** August 2026  
**API Version:** 1.0
