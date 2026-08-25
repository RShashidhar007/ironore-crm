"""
Test script to debug complaint solution generation.
Run this to see what's happening with your current complaint data.
"""
import sys
sys.path.insert(0, '/projects/ironore-crm/backend')

from app.database import SessionLocal
from app.models import ComplaintMaster

def test_complaint_generation(complaint_id=None):
    db = SessionLocal()
    
    if complaint_id:
        complaint = db.query(ComplaintMaster).filter(
            ComplaintMaster.ComplaintID == complaint_id
        ).first()
        if not complaint:
            print("Complaint {} not found".format(complaint_id))
            return
    else:
        # Get the latest complaint
        complaint = db.query(ComplaintMaster).order_by(ComplaintMaster.CreatedDate.desc()).first()
    
    if not complaint:
        print("No complaints found in database")
        return
    
    print("\n[Complaint Details]")
    print("ID: {}".format(complaint.ComplaintID))
    print("Status: {}".format(complaint.Status))
    print("Category: {}".format(complaint.CategoryType))
    print("Description: {}...".format(complaint.ComplaintDescription[:80]))
    
    print("\n[Auto-Generation Conditions]")
    
    # Check condition 1 - Marketing has content
    has_marketing_review = complaint.MarketingReview and complaint.MarketingReview.strip()
    print("1. Marketing Review Exists: {}".format(has_marketing_review))
    print("   Value: '{}'".format(complaint.MarketingReview))
    
    # Check condition 2 - Plant Head has content
    has_plant_review = complaint.PlantHeadReview and complaint.PlantHeadReview.strip()
    print("2. Plant Head Review Exists: {}".format(has_plant_review))
    print("   Value: '{}'".format(complaint.PlantHeadReview))
    
    # Check condition 3
    has_rca = complaint.RootCauseAnalysis and complaint.RootCauseAnalysis.strip()
    print("3. RCA Exists: {}".format(has_rca))
    if has_rca:
        print("   Value: {}...".format(complaint.RootCauseAnalysis[:60]))
    
    # Check condition 4
    has_capa = complaint.CorrectivePreventiveAction and complaint.CorrectivePreventiveAction.strip()
    print("4. CAPA Exists: {}".format(has_capa))
    if has_capa:
        print("   Value: {}...".format(complaint.CorrectivePreventiveAction[:60]))
    
    # Check condition 5
    has_solution = complaint.Solution and complaint.Solution.strip()
    print("5. Solution Already Exists: {}".format(has_solution))
    
    print("\n[RESULT]")
    all_met = has_marketing_review and has_plant_review and has_rca and has_capa
    print("All conditions met: {}".format(all_met))
    print("Current solution: {}".format(complaint.Solution[:100] if complaint.Solution else 'NULL'))
    
    db.close()

if __name__ == "__main__":
    complaint_id = sys.argv[1] if len(sys.argv) > 1 else None
    test_complaint_generation(complaint_id)

