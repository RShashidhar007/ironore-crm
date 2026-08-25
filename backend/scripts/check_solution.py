import sys
sys.path.insert(0, '/projects/ironore-crm/backend')
from app.database import SessionLocal
from app.models import ComplaintMaster

db = SessionLocal()
c = db.query(ComplaintMaster).filter(ComplaintMaster.ComplaintID == 'CMP-20260825-0003').first()
if c:
    has_solution = bool(c.Solution and str(c.Solution).strip())
    print(f'CMP-20260825-0003:')
    print(f'Solution exists: {has_solution}')
    print(f'Updated: {c.UpdatedDate}')
    print(f'Status: {c.Status}')
    if has_solution:
        print(f'Solution (first 200 chars): {str(c.Solution)[:200]}')
    else:
        print('Solution is NULL or empty')
db.close()
