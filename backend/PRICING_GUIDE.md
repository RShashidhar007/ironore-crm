o# Iron Ore CRM - Pricing Guide

## Price Units

All prices in the Iron Ore CRM system are stored as **per Metric Ton (MT)** unless otherwise specified.

### Price Fields in Inventory Master

The `Inventory_Master` table has two price fields:

#### 1. **InitialPrice** (Base/Cost Price per MT)
- Represents the base cost or initial production cost per Metric Ton
- Example: `4500` means **4,500 INR per MT** (or per unit in your currency)
- Used for cost tracking and margin calculations
- Always filled for "Produced" entries

#### 2. **SellingPrice** (Sales Price per MT)
- Represents the market/selling price per Metric Ton
- Example: `5200` means **5,200 INR per MT** (or per unit in your currency)
- May be NULL for "Produced" entries (not yet sold)
- Filled when an order is placed ("Sold" entry created)

### Data Model Example

```
InventoryID | PID     | Category  | QuantityMT | InitialPrice | SellingPrice | ProducedDate
------------|---------|-----------|------------|--------------|--------------|-------------
1           | 13000000| Produced  | 500        | 4500         | NULL         | 2026-08-01
2           | 13000000| Sold      | 150        | 4500         | 5200         | 2026-08-01
```

**Interpretation:**
- 500 MT of product 13000000 was produced at 4,500 INR/MT cost
- 150 MT was sold at 5,200 INR/MT selling price
- Available stock = 500 - 150 = 350 MT

## Calculation Examples

### Total Order Cost
```
Total Cost = Quantity (MT) × SellingPrice (per MT)

Example:
- Customer orders 100 MT
- SellingPrice = 5,200 INR/MT
- Total Cost = 100 × 5,200 = 520,000 INR
```

### Profit Margin
```
Profit per MT = SellingPrice - InitialPrice

Example:
- InitialPrice = 4,500 INR/MT
- SellingPrice = 5,200 INR/MT
- Profit per MT = 5,200 - 4,500 = 700 INR/MT

Total Profit on 100 MT order:
- Total Profit = 100 × 700 = 70,000 INR
```

### Stock Availability
```
Available = SUM(Produced QuantityMT) - SUM(Sold QuantityMT)

Query:
SELECT 
    PID,
    SUM(CASE WHEN Category = 'Produced' THEN QuantityMT ELSE 0 END) as Produced,
    SUM(CASE WHEN Category = 'Sold' THEN QuantityMT ELSE 0 END) as Sold,
    SUM(CASE WHEN Category = 'Produced' THEN QuantityMT ELSE -QuantityMT END) as Available
FROM Inventory_Master
GROUP BY PID
```

## Frontend Display

When displaying prices to customers or in the chat interface:

```python
# Format function (from chat.py)
def format_price_per_mt(price: int, currency: str = "INR") -> str:
    """Example: 4500 INR/MT"""
    return f"{price:,} {currency}/MT"

# Usage:
initial_price_str = format_price_per_mt(4500)  # Output: "4,500 INR/MT"
selling_price_str = format_price_per_mt(5200)  # Output: "5,200 INR/MT"
```

## Database Schema

### Inventory_Master Table

```sql
CREATE TABLE [dbo].[Inventory_Master] (
    [InventoryID] INT PRIMARY KEY IDENTITY(1,1),
    [PID] VARCHAR(50) FOREIGN KEY REFERENCES [Product_Master]([PID]),
    [Category] VARCHAR(100),           -- 'Produced' or 'Sold'
    [QuantityMT] DECIMAL(10,2),        -- Quantity in Metric Tons
    [ProducedDate] DATE,
    [InitialPrice] DECIMAL(10,2),      -- Price per MT
    [SellingPrice] DECIMAL(10,2)       -- Price per MT (NULL if not yet sold)
);
```

## Business Rules

1. **InitialPrice is always filled** for Produced entries
2. **SellingPrice may be NULL** for Produced entries (not yet sold)
3. **Both prices filled** for Sold entries (order placed)
4. **Unit is always MT** - no conversions needed if this is maintained consistently
5. **Prices are per MT** - not per shipment or per order

## API Integration

When the API returns inventory information, it includes:

```json
{
    "product_id": "13000000",
    "product_name": "LOW CCS IRON ORE PELLET",
    "available_quantity_mt": 350,
    "initial_price_per_mt": 4500,
    "selling_price_per_mt": 5200,
    "currency": "INR"
}
```

## Price Negotiations

During order placement:
1. Customer requests quantity in MT
2. System checks availability
3. If available, order is created with current SellingPrice per MT
4. Company executive contacts customer for:
   - Final price negotiations (may adjust per MT price)
   - Delivery timeline
   - Payment terms

---

**Last Updated:** August 2026  
**Version:** 1.0  
**Currency:** INR (configurable via environment variables)
