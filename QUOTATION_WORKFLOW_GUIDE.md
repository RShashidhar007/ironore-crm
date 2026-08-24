# Quotation Workflow - Complete Guide

## Overview

The improved quotation workflow now follows a 3-step process:
1. **Show Products** - Display all products with available inventory
2. **Select Product** - Customer selects desired product  
3. **Enter Quantity** - Customer specifies quantity and system generates quotation

## Complete User Flow

```
User Interface Flow:

Step 1: Click "Ask for a Quotation"
   ↓
Step 2: See Product List
   ├─ Product 1: 350 MT available
   ├─ Product 2: 220 MT available
   ├─ Product 3: 250 MT available
   └─ [Product buttons for selection]
   ↓
Step 3: Click Product (Select Product)
   ├─ Shows selected product
   ├─ Shows available inventory quantity
   └─ Asks for desired quantity (input field)
   ↓
Step 4: Enter Quantity
   ├─ System validates quantity ≤ available
   ├─ If valid: Generate quotation
   ├─ If invalid: Show error & available amount
   └─ Show quotation with PDF link
   ↓
Step 5: Download & Review
   ├─ Text quotation in chat
   ├─ PDF quotation download
   ├─ Price history included
   └─ Pricing based on last 2-3 sales
```

## Backend API Actions

### Action 1: Initial Quotation Request
```
Intent: QUOTATION_REQUEST
Action: (none - initial request)
```

**Backend Response:**
```json
{
  "reply": "Hello [Customer], I can help you generate a quotation!

**Available Products in Stock:**
• Product 1 (ID: 13000000)
• Product 2 (ID: 13000001)
...

Please click on a product below to select it, then I'll ask for the quantity.",

  "structured_data": {
    "products": [
      {"pid": "13000000", "name": "Product 1", "id": 0},
      {"pid": "13000001", "name": "Product 2", "id": 1}
    ],
    "status": "awaiting_product_selection"
  }
}
```

### Action 2: Product Selection
```
Action: "select_product_quotation:0"
         (0 = index of product in list)
```

**Backend Response:**
```json
{
  "reply": "Great! You selected **Product 1**

**Available Stock:** 350.00 MT

Please enter the quantity you need (in MT):
*Example: 50 or 100.5*",

  "structured_data": {
    "product_id": "13000000",
    "product_name": "Product 1",
    "available_quantity": 350.0,
    "status": "awaiting_quantity"
  }
}
```

### Action 3: Quantity Submission
```
Action: "submit_quantity_quotation:13000000:100"
         (PID:QUANTITY)
```

**Backend Response (Success):**
```json
{
  "reply": "QUOTATION GENERATED

Quotation Number: QT-2026-08-24-001
Generated Date: 24-08-2026 15:30
Valid Till: 31-08-2026
Validity: 7 days

PRODUCT DETAILS:
Product: Product 1
Quantity: 100.00 MT
Unit Price: ₹ 5,150.00 per MT
TOTAL AMOUNT: ₹ 515,000.00

Recent Price History (Last 2-3 Sales):
• Sale 1: ₹ 5,200.00/MT on 24-08-2026
• Sale 2: ₹ 5,150.00/MT on 20-08-2026
• Sale 3: ₹ 5,100.00/MT on 15-08-2026

A detailed PDF quotation has been generated.

[Download PDF] [View Details] [New Quotation]",

  "structured_data": {
    "quotation_id": 1,
    "quotation_number": "QT-2026-08-24-001",
    "product_id": "13000000",
    "quantity_mt": 100.0,
    "price_per_mt": 5150.0,
    "total_amount": 515000.0,
    "pdf_path": "quotations/QT-2026-08-24-001_20260824_153022.pdf",
    "status": "quotation_generated"
  }
}
```

**Backend Response (Insufficient Quantity):**
```json
{
  "reply": "Only 350.00 MT available, but you requested 400.00 MT.

Would you like to order 350.00 MT instead?",

  "structured_data": {
    "product_id": "13000000",
    "requested_quantity": 400.0,
    "available_quantity": 350.0,
    "status": "insufficient_quantity"
  }
}
```

## Data Models

### Quotations Created in Database

```
QuotationID: 1
QuotationNumber: QT-2026-08-24-001
CID: CUST001 (Customer ID)
PID: 13000000 (Product ID)
ProductName: Product 1
QuantityMT: 100.00
PricePerMT: 5150.00 (Average of last 3 sales)
TotalAmount: 515000.00 (Quantity × Price)
ValidityDays: 7
Status: Generated
CreatedDate: 2026-08-24 15:30:22
ExpiryDate: 2026-08-31 15:30:22
PDFFilePath: quotations/QT-2026-08-24-001_20260824_153022.pdf
```

### Inventory Master Tracking

```
# Before Quotation
InventoryID | PID      | Category  | QuantityMT | InitialPrice | SellingPrice
1           | 13000000 | Produced  | 500        | 5100         | NULL
2           | 13000000 | Sold      | 150        | 5100         | 5200

Available: 500 - 150 = 350 MT

# After Creating Quotation (no changes to inventory)
# Quotation is created with current prices
# Inventory is NOT deducted (only when order is placed)
```

### Price Calculation

```
Step 1: Get last 3 selling prices for product
  Query: SELECT TOP 3 SellingPrice FROM Inventory_Master
         WHERE PID = '13000000' AND Category = 'Sold'
         ORDER BY ProducedDate DESC
  
  Result: [5200.00, 5150.00, 5100.00]

Step 2: Calculate average
  Average = (5200 + 5150 + 5100) / 3 = 5150.00 INR/MT

Step 3: Calculate total
  Total = 100 MT × 5150 INR/MT = 515,000.00 INR

Step 4: Create quotation with this pricing
```

## Frontend Implementation

### Component Flow

```
ChatWidget
├─ Display initial message with product list
├─ Create product buttons/cards from structured_data
│  └─ Each button → action: "select_product_quotation:0"
├─ On button click: Send action to chat API
├─ Receive product selection response
├─ Display quantity input field
├─ On quantity submit: Send action "submit_quantity_quotation:PID:QTY"
├─ Receive quotation response
├─ Display quotation summary
├─ Show PDF download button
└─ Show action buttons: [Download PDF], [New Quotation]
```

### Key Properties from structured_data

```javascript
// Step 1: Initial response
structured_data.products = [
  { pid: "13000000", name: "Product 1", id: 0 }
]
structured_data.status = "awaiting_product_selection"

// Step 2: After product selection
structured_data.product_id = "13000000"
structured_data.product_name = "Product 1"
structured_data.available_quantity = 350.0
structured_data.status = "awaiting_quantity"

// Step 3: After quotation generated
structured_data.quotation_id = 1
structured_data.quotation_number = "QT-2026-08-24-001"
structured_data.total_amount = 515000.0
structured_data.pdf_path = "quotations/QT-2026-08-24-001_..."
structured_data.status = "quotation_generated"
```

## Error Handling

### Error: Invalid Product Index
```
User sends: select_product_quotation:999 (invalid index)
Response: "Invalid product selection. Please try again."
```

### Error: Invalid Quantity Format
```
User sends: submit_quantity_quotation:13000000:abc
Response: "Invalid quantity. Please enter a valid number."
```

### Error: Zero or Negative Quantity
```
User sends: submit_quantity_quotation:13000000:0
Response: "Quantity must be greater than 0. Please try again."
```

### Error: Insufficient Inventory
```
User sends: submit_quantity_quotation:13000000:500 (only 350 available)
Response: "Only 350.00 MT available, but you requested 500.00 MT.
          Would you like to order 350.00 MT instead?"
Status: insufficient_quantity
```

## Database Tables Updated

### Quotations_Master Table
```sql
-- New quotation record created for each generated quotation
INSERT INTO Quotations_Master (
  QuotationNumber, CID, PID, ProductName,
  QuantityMT, PricePerMT, TotalAmount,
  ValidityDays, Status,
  CreatedBy, CreatedDate, ExpiryDate,
  PDFFilePath
)
VALUES (
  'QT-2026-08-24-001', 'CUST001', '13000000', 'Product 1',
  100.00, 5150.00, 515000.00,
  7, 'Generated',
  'user001', '2026-08-24 15:30:22', '2026-08-31 15:30:22',
  'quotations/QT-2026-08-24-001_20260824_153022.pdf'
)
```

### Inventory_Master (No changes)
```
-- Inventory is NOT modified when quotation is created
-- Only modified when ORDER is placed
-- Quotations are non-binding estimates
```

## PDF Quotation Contents

Each generated PDF includes:

**Header Section:**
- Quotation title
- Quotation number: QT-2026-08-24-001
- Issue date: 24-08-2026
- Valid till: 31-08-2026
- Validity: 7 days

**Customer Section:**
- Company name
- Contact person
- Email
- Mobile
- Address

**Product Table:**
- Description: Product 1
- Quantity: 100.00 MT
- Unit price: ₹ 5,150.00/MT
- Amount: ₹ 515,000.00

**Price History Table:**
- Date | Price/MT
- 24-08-2026 | ₹ 5,200.00
- 20-08-2026 | ₹ 5,150.00
- 15-08-2026 | ₹ 5,100.00

**Terms & Footer:**
- Quote valid for 7 days
- For price negotiations, contact sales
- Thank you message

## API Endpoints

### Generate Quotation (Step 3)
```
POST /api/quotations/generate
Parameters:
  - product_id: "13000000"
  - quantity_mt: 100.0
  - notes: (optional)
```

### Get Quotation
```
GET /api/quotations/{quotation_id}
Returns: Full quotation details
```

### Download PDF
```
GET /api/quotations/{quotation_id}/pdf
Returns: PDF file (application/pdf)
```

### List Quotations
```
GET /api/quotations
Returns: All customer's quotations
```

## Testing Checklist

- [ ] Click "Ask for Quotation" shows products with available quantity
- [ ] Each product shows as a button/card
- [ ] Click product shows selected product details
- [ ] Shows available quantity for selected product
- [ ] Input quantity validation works
- [ ] Quantity > 0 validation works
- [ ] Quantity ≤ available validation works
- [ ] Quotation generates successfully
- [ ] PDF downloads and opens
- [ ] Price history shows last 3 sales
- [ ] Quotation stored in database
- [ ] Error messages display properly
- [ ] Insufficient quantity handled correctly
- [ ] Multiple quotations can be created

## Summary

✅ **Improved Quotation Workflow**
- Products displayed with available inventory
- Step-by-step selection process
- Quantity validation against inventory
- Professional quotation generation with PDF
- Full audit trail in database
- Price history-based pricing
- Error handling for all scenarios

---

**Updated:** August 24, 2026  
**Status:** ✅ Complete  
**Version:** 2.0 - Improved UX Flow
