"""Check specific complaint details"""
import sys
sys.path.insert(0, '/projects/ironore-crm/backend')

from app.database import SessionLocal
from app.models import ComplaintMaster

db = SessionLocal()
try:
    complaint = db.query(ComplaintMaster).filter(ComplaintMaster.ComplaintID == 'CMP-20260824-0001').first()
    
    if complaint:
        print(f"\nComplaint: {complaint.ComplaintID}")
        print(f"Updated Date: {complaint.UpdatedDate}")
        print(f"\nMarketing Review:")
        print(f"  Value: {complaint.MarketingReview}")
        print(f"  Has content: {bool(complaint.MarketingReview and str(complaint.MarketingReview).strip())}")
        print(f"\nPlant Head Review:")
        print(f"  Value: {complaint.PlantHeadReview}")
        print(f"  Has content: {bool(complaint.PlantHeadReview and str(complaint.PlantHeadReview).strip())}")
        print(f"\nRCA:")
        print(f"  Value: {complaint.RootCauseAnalysis[:100] if complaint.RootCauseAnalysis else 'NULL'}")
        print(f"  Has content: {bool(complaint.RootCauseAnalysis and str(complaint.RootCauseAnalysis).strip())}")
        print(f"\nCPA:")
        print(f"  Value: {complaint.CorrectivePreventiveAction[:100] if complaint.CorrectivePreventiveAction else 'NULL'}")
        print(f"  Has content: {bool(complaint.CorrectivePreventiveAction and str(complaint.CorrectivePreventiveAction).strip())}")
        print(f"\nSolution:")
        print(f"  Value: {complaint.Solution[:100] if complaint.Solution else 'NULL'}")
        print(f"  Has content: {bool(complaint.Solution and str(complaint.Solution).strip())}")
        
        # Check all conditions
        has_all = (
            complaint.MarketingReview and str(complaint.MarketingReview).strip() and
            complaint.PlantHeadReview and str(complaint.PlantHeadReview).strip() and
            complaint.RootCauseAnalysis and str(complaint.RootCauseAnalysis).strip() and
            complaint.CorrectivePreventiveAction and str(complaint.CorrectivePreventiveAction).strip()
        )
        
        needs_solution = not complaint.Solution or not str(complaint.Solution).strip()
        
        print(f"\nAll conditions met: {has_all}")
        print(f"Needs solution: {needs_solution}")
        print(f"Ready for generation: {has_all and needs_solution}")
    else:
        print("Complaint not found!")
        
finally:
    db.close()
