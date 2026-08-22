"""
Check all complaints and show their current data status
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import ComplaintMaster

db = SessionLocal()

# Get all complaints
complaints = db.query(ComplaintMaster).order_by(ComplaintMaster.CreatedDate.desc()).all()

print("="*80)
print("COMPLAINT STATUS REPORT")
print("="*80)
print(f"Total Complaints: {len(complaints)}\n")

for c in complaints:
    print(f"Complaint ID: {c.ComplaintID}")
    print(f"  Category: {c.CategoryType or 'NULL'}")
    print(f"  Description: {c.ComplaintDescription[:50] if c.ComplaintDescription else 'NULL'}...")
    print(f"  Summary: {'✓ Present' if c.Summary else '✗ NULL'}")
    print(f"  Solution: {'✓ Present' if c.Solution else '✗ NULL'}")
    print(f"  Progress: {'✓ Present' if c.Progress else '✗ NULL'}")
    print(f"  Status: {c.Status or 'NULL'}")
    print(f"  PO Number: {c.PONumber or 'NULL'}")
    print(f"  Dispatch Date: {c.DispatchDate or 'NULL'}")
    print(f"  Created: {c.CreatedDate.strftime('%Y-%m-%d %H:%M') if c.CreatedDate else 'NULL'}")
    
    # Check if has all required fields
    has_all = c.Summary and c.Solution and c.Progress and c.Status
    print(f"  Complete: {'✓ YES' if has_all else '✗ NO - Missing data'}")
    print("-"*80)

db.close()
