"""
Populate inventory master with sample data
Format: 
- Produced: Shows quantity produced with InitialPrice, SellingPrice=NULL
- Sold: Shows quantity sold with both InitialPrice and SellingPrice
"""

from app.database import SessionLocal
from app.models import InventoryMaster
from datetime import date

db = SessionLocal()

# Sample data to insert
inventory_data = [
    # Product 13000000 - Iron Ore Fines
    {'PID': '13000000', 'Category': 'Produced', 'QuantityMT': 500.00, 'ProducedDate': date(2026, 8, 1), 'InitialPrice': 4500.00, 'SellingPrice': None},
    {'PID': '13000000', 'Category': 'Sold', 'QuantityMT': 150.00, 'ProducedDate': date(2026, 8, 1), 'InitialPrice': 4500.00, 'SellingPrice': 5200.00},
    
    # Product 13000001 - Iron Ore Lumps
    {'PID': '13000001', 'Category': 'Produced', 'QuantityMT': 300.00, 'ProducedDate': date(2026, 8, 3), 'InitialPrice': 4300.00, 'SellingPrice': None},
    {'PID': '13000001', 'Category': 'Sold', 'QuantityMT': 80.00, 'ProducedDate': date(2026, 8, 3), 'InitialPrice': 4300.00, 'SellingPrice': 5000.00},
    
    # Product 13000002 - Iron Pellets FE 63
    {'PID': '13000002', 'Category': 'Produced', 'QuantityMT': 450.00, 'ProducedDate': date(2026, 8, 5), 'InitialPrice': 8500.00, 'SellingPrice': None},
    {'PID': '13000002', 'Category': 'Sold', 'QuantityMT': 200.00, 'ProducedDate': date(2026, 8, 5), 'InitialPrice': 8500.00, 'SellingPrice': 9500.00},
    
    # Product 13000003 - Iron Pellets FE 65
    {'PID': '13000003', 'Category': 'Produced', 'QuantityMT': 300.00, 'ProducedDate': date(2026, 8, 8), 'InitialPrice': 8600.00, 'SellingPrice': None},
    {'PID': '13000003', 'Category': 'Sold', 'QuantityMT': 250.00, 'ProducedDate': date(2026, 8, 8), 'InitialPrice': 8600.00, 'SellingPrice': 9700.00},
    
    # Product 13000004 - Iron Ore Pellet FE 60-65
    {'PID': '13000004', 'Category': 'Produced', 'QuantityMT': 400.00, 'ProducedDate': date(2026, 8, 10), 'InitialPrice': 8400.00, 'SellingPrice': None},
    {'PID': '13000004', 'Category': 'Sold', 'QuantityMT': 125.00, 'ProducedDate': date(2026, 8, 10), 'InitialPrice': 8400.00, 'SellingPrice': 9400.00},
]

try:
    # Clear existing data (optional)
    db.query(InventoryMaster).delete()
    db.commit()
    print("Cleared existing inventory data")
    
    # Insert new data
    for item in inventory_data:
        inventory = InventoryMaster(
            PID=item['PID'],
            Category=item['Category'],
            QuantityMT=item['QuantityMT'],
            ProducedDate=item['ProducedDate'],
            InitialPrice=item['InitialPrice'],
            SellingPrice=item['SellingPrice']
        )
        db.add(inventory)
    
    db.commit()
    print(f"Successfully inserted {len(inventory_data)} inventory records")
    
    # Display inventory summary
    print("\n--- Inventory Summary (Available Stock = Produced - Sold) ---")
    from sqlalchemy import func, case
    summary = db.query(
        InventoryMaster.PID,
        func.sum(
            case(
                (InventoryMaster.Category == 'Produced', InventoryMaster.QuantityMT),
                else_=0
            )
        ).label('produced'),
        func.sum(
            case(
                (InventoryMaster.Category == 'Sold', InventoryMaster.QuantityMT),
                else_=0
            )
        ).label('sold'),
        func.sum(
            case(
                (InventoryMaster.Category == 'Produced', InventoryMaster.QuantityMT),
                else_=-InventoryMaster.QuantityMT
            )
        ).label('available')
    ).group_by(InventoryMaster.PID).all()
    
    for row in summary:
        print(f"PID: {row.PID} | Produced: {row.produced} MT | Sold: {row.sold} MT | Available: {row.available} MT")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
