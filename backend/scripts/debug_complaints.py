"""Debug script to see all complaints and their status"""
import sys
sys.path.insert(0, '/projects/ironore-crm/backend')

from app.database import SessionLocal
from app.models import ComplaintMaster

db = SessionLocal()
try:
    complaints = db.query(ComplaintMaster).all()
    print(f"\nTotal complaints in DB: {len(complaints)}\n")
    
    for c in complaints:
        print(f"ID: {c.ComplaintID}")
        print(f"  Marketing: {'YES' if c.MarketingReview and str(c.MarketingReview).strip() else 'NO'} - {str(c.MarketingReview)[:50] if c.MarketingReview else 'NULL'}")
        print(f"  Plant Head: {'YES' if c.PlantHeadReview and str(c.PlantHeadReview).strip() else 'NO'} - {str(c.PlantHeadReview)[:50] if c.PlantHeadReview else 'NULL'}")
        print(f"  RCA: {'YES' if c.RootCauseAnalysis and str(c.RootCauseAnalysis).strip() else 'NO'} - {str(c.RootCauseAnalysis)[:50] if c.RootCauseAnalysis else 'NULL'}")
        print(f"  CAPA: {'YES' if c.CorrectivePreventiveAction and str(c.CorrectivePreventiveAction).strip() else 'NO'} - {str(c.CorrectivePreventiveAction)[:50] if c.CorrectivePreventiveAction else 'NULL'}")
        print(f"  Solution: {'YES' if c.Solution and str(c.Solution).strip() else 'NO'}")
        print()
finally:
    db.close()
