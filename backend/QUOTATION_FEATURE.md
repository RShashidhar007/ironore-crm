# Quotation Generation Feature

## Overview

The quotation generation feature allows customers to request automated quotations for iron ore and iron pellet products. The system:

1. Asks customer for product and quantity
2. Retrieves pricing history (last 2-3 sales)
3. Calculates average price
4. Generates professional PDF quotation
5. Provides text quotation in chat
6. Stores quotation in database for tracking

## User Workflow

### Step 1: Click "Ask for a Quotation"
Customer clicks the action button in the chat interface.

### Step 2: System Lists Available Products
```
Available Products:
• LOW CCS IRON ORE PELLET (ID: 13000000)
• Unscreened Accretion (ID: 13000001)
• IRON ORE PELLET FE 63 (ID: 13000002)
• [more products...]

Please provide:
1. Product name or ID
2. Quantity needed (in Metric Tons)
3. Any special notes (optional)
```

### Step 3: Customer Provides Details
Customer sends message with:
- Product ID or name
- Quantity in MT
- Optional notes

### Step 4: Quotation Generated
System:
1. Validates product exists
2. Retrieves last 2-3 selling prices
3. Calculates average price per MT
4. Creates quotation record
5. Generates PDF with:
   - Quotation number
   - Product details
   - Pricing breakdown
   - Price history
   - Terms & validity
6. Returns text quotation in chat + PDF download link

### Step 5: Customer Reviews & Accepts
Customer can:
- Download PDF quotation
- Accept quotation (initiates order process)
- Request modifications
- Forward to management

## Pricing Calculation

### Price History Retrieval
```python
# Get last 3 sales for product
sales = [
    (5200.00, '2026-08-15'),  # Most recent
    (5150.00, '2026-08-08'),
    (5100.00, '2026-08-01'),
]

# Calculate average
average_price = (5200 + 5150 + 5100) / 3 = 5150.00 INR/MT
```

### Total Quotation Amount
```
Total = Quantity (MT) × Price per MT
Total = 100 MT × 5150 INR/MT = 515,000 INR
```

## Database Schema

### Quotations_Master Table

```sql
CREATE TABLE [dbo].[Quotations_Master] (
    [QuotationID] INT PRIMARY KEY IDENTITY(1,1),
    [QuotationNumber] VARCHAR(50) UNIQUE NOT NULL,  -- QT-2026-08-001
    [CID] VARCHAR(50),                              -- Customer ID
    [PID] VARCHAR(50),                              -- Product ID
    [ProductName] VARCHAR(250),
    [QuantityMT] DECIMAL(10,2),                     -- Quantity requested
    [PricePerMT] DECIMAL(10,2),                     -- Quoted price/MT
    [TotalAmount] DECIMAL(12,2),                    -- Total: Qty × Price
    [ValidityDays] INT DEFAULT 7,                   -- Quote valid for N days
    [Notes] TEXT,                                   -- Additional terms
    [Status] VARCHAR(50),                           -- Generated/Accepted/Rejected
    [CreatedBy] VARCHAR(100),
    [CreatedDate] DATETIME,
    [ExpiryDate] DATETIME,
    [AcceptedDate] DATETIME,
    [PDFFilePath] VARCHAR(500),                     -- PDF file location
    [UpdatedBy] VARCHAR(100),
    [UpdatedDate] DATETIME
);
```

## API Endpoints

### Generate Quotation
```
POST /api/quotations/generate

Query Parameters:
- product_id: string (required) - Product PID
- quantity_mt: float (required) - Quantity in MT
- notes: string (optional) - Additional notes
- validity_days: int (optional, default=7) - Validity period

Response:
{
  "reply": "Quotation generated text...",
  "action_buttons": ["Download PDF", "View Details", "Modify Quotation"],
  "structured_data": {
    "quotation_id": 1,
    "quotation_number": "QT-2026-08-001",
    "product_id": "13000000",
    "quantity_mt": 100.0,
    "price_per_mt": 5150.00,
    "total_amount": 515000.00,
    "pdf_path": "quotations/QT-2026-08-001_20260815_143022.pdf",
    "expiry_date": "2026-08-22T00:00:00"
  }
}
```

### Get Quotation Details
```
GET /api/quotations/{quotation_id}

Response:
{
  "quotation_id": 1,
  "quotation_number": "QT-2026-08-001",
  "product_name": "LOW CCS IRON ORE PELLET",
  "quantity_mt": 100.0,
  "price_per_mt": 5150.00,
  "total_amount": 515000.00,
  "status": "Generated",
  "created_date": "2026-08-15T14:30:22",
  "expiry_date": "2026-08-22T00:00:00",
  "pdf_path": "quotations/QT-2026-08-001_20260815_143022.pdf"
}
```

### Download Quotation PDF
```
GET /api/quotations/{quotation_id}/pdf

Response: PDF file (application/pdf)
```

### List Customer's Quotations
```
GET /api/quotations

Response:
{
  "quotations": [
    {
      "quotation_id": 1,
      "quotation_number": "QT-2026-08-001",
      "product_name": "LOW CCS IRON ORE PELLET",
      "quantity_mt": 100.0,
      "total_amount": 515000.00,
      "status": "Generated",
      "created_date": "2026-08-15T14:30:22",
      "expiry_date": "2026-08-22T00:00:00"
    },
    ...
  ]
}
```

## Chat Integration

### Action Button Flow

```
User clicks "Ask for a Quotation"
    ↓
Chat shows available products
    ↓
User sends product ID + quantity
    ↓
Action parsed: generate_quotation:PID:QUANTITY:NOTES
    ↓
Quotation service generates quotation
    ↓
PDF created and saved
    ↓
Response: Text quotation + action buttons
    ↓
User can download PDF or proceed
```

### Example Chat Flow

**User:** "Ask for a Quotation"

**Bot:**
```
Hello [Customer], I can help you with a quotation.

Available Products:
• LOW CCS IRON ORE PELLET (ID: 13000000)
• Unscreened Accretion (ID: 13000001)
• IRON ORE PELLET FE 63 (ID: 13000002)

Please provide:
1. Product name or ID
2. Quantity needed (in Metric Tons)
3. Any special notes (optional)
```

**User:** "13000000, 100 MT, FOB Port Chennai"

**Bot:**
```
QUOTATION GENERATED

Quotation Number: QT-2026-08-001
Generated Date: 15-08-2026 14:30
Valid Till: 22-08-2026
Validity: 7 days

PRODUCT DETAILS:
Product: LOW CCS IRON ORE PELLET
Quantity: 100.00 MT
Unit Price: ₹ 5,150.00 per MT
TOTAL AMOUNT: ₹ 515,000.00

Recent Price History (Last 2-3 Sales):
• Sale 1: ₹ 5,200.00/MT on 15-08-2026
• Sale 2: ₹ 5,150.00/MT on 08-08-2026
• Sale 3: ₹ 5,100.00/MT on 01-08-2026

A detailed PDF quotation has been generated and is attached.

NEXT STEPS:
Please review this quotation and let us know if you have any questions.
Our sales team will contact you shortly to confirm your order.

[Download PDF] [View Details] [Modify Quotation]
```

## PDF Quotation Contents

The generated PDF includes:

1. **Header**
   - "QUOTATION" title
   - Quotation number
   - Date issued
   - Validity period

2. **Bill To**
   - Customer name
   - Contact person
   - Email
   - Mobile
   - Address

3. **Product Details Table**
   - Product name
   - Quantity (MT)
   - Unit price (per MT)
   - Total amount

4. **Price History**
   - Last 2-3 sales with dates
   - Previous prices for reference

5. **Terms & Notes**
   - Validity period
   - Delivery terms (if any)
   - Payment terms (if any)
   - Additional notes

6. **Footer**
   - Validity notice
   - Call to action
   - Thank you message

## Features

✅ **Automatic Price Averaging**: Uses last 2-3 sales to calculate fair price
✅ **Professional PDF**: Branded quotation with all details
✅ **Pricing Transparency**: Shows price history for customer reference
✅ **Quotation Tracking**: All quotations stored in database
✅ **Expiry Management**: Quotes expire after N days (configurable)
✅ **Chat Integration**: Seamless in-chat quotation generation
✅ **Customer History**: Customers can view all their quotations
✅ **PDF Download**: Professional PDF for records/forwarding

## Configuration

### Quotation Defaults

In `config.py`:
```python
QUOTATION_VALIDITY_DAYS = 7  # Default validity
QUOTATION_PRICE_HISTORY_LIMIT = 3  # Last N prices to average
QUOTATION_PDF_SAVE_DIR = "quotations"  # PDF storage location
```

### Database Setup

Run migration script:
```bash
# SQL Server
sqlcmd -S your_server -U username -P password -d Customer_DB -i database/create_quotations_table.sql

# Or via Python
python -m app.seed_data  # Creates table if needed
```

## Error Handling

| Error | Response |
|-------|----------|
| Product not found | "Product {id} not found" |
| Invalid quantity | "Quantity must be greater than 0" |
| No price history | Uses InitialPrice from inventory |
| PDF generation fails | Returns error message, no quotation created |
| Customer not linked | "Customer ID not found" |

## Future Enhancements

- [ ] Email quotation directly to customer
- [ ] Bulk quotations (multiple products)
- [ ] Discounts & volume pricing tiers
- [ ] Quotation approval workflow
- [ ] Automatic order conversion
- [ ] Quotation expiry notifications
- [ ] Multi-language PDF support
- [ ] Digital signature support

---

**Last Updated:** August 2026  
**Version:** 1.0  
**Status:** Fully Functional
