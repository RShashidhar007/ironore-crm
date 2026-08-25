"""Test with a new complaint to verify solution generation works"""
import sys
sys.path.insert(0, '/projects/ironore-crm/backend')

from datetime import datetime
from app.database import SessionLocal
from app.models import ComplaintMaster
from app.routers.complaint import regenerate_solution_if_conditions_met

db = SessionLocal()
try:
    # Create a test complaint with all fields but NO solution
    test_complaint = ComplaintMaster(
        ComplaintID='TEST-REGEN-001',
        CategoryType='Quality',
        ComplaintDescription='Test complaint for solution regeneration',
        MarketingReview='Approved by marketing team for testing',
        PlantHeadReview='Plant operations team approves this test',
        RootCauseAnalysis='Test shows the root cause is improper handling',
        CorrectivePreventiveAction='Implement new procedures to prevent this issue',
        Status='Under Review',
        CreatedBy='Test User',
        CreatedDate=datetime.now(),
        Solution=None  # No solution yet
    )
    
    db.add(test_complaint)
    db.commit()
    
    print(f"\n[Test Complaint Created]")
    print(f"ID: {test_complaint.ComplaintID}")
    print(f"Before: Solution = {test_complaint.Solution}")
    
    # Try to regenerate
    print(f"\n[Attempting Solution Generation]")
    success = regenerate_solution_if_conditions_met(test_complaint)
    
    if success:
        db.commit()
        print(f"SUCCESS - Solution generated!")
        print(f"After: Solution = {test_complaint.Solution[:100] if test_complaint.Solution else 'NULL'}")
    else:
        print(f"FAILED - Conditions not met or generation failed")
        
finally:
    db.close()
