"""
Test script to debug complaint solution generation.
Run this to see what's happening with your current complaint data.
"""
import sys
sys.path.insert(0, '/projects/ironore-crm/backend')

from app.database import SessionLocal
from app.models import ComplaintMaster

def test_complaint_generation():
    db = SessionLocal()
    
    # Get the latest complaint
    complaint = db.query(ComplaintMaster).order_by(ComplaintMaster.CreatedDate.desc()).first()
    
    if not complaint:
        print("❌ No complaints found in database")
        return
    
    print(f"\n📋 Complaint: {complaint.ComplaintID}")
    print(f"   Status: {complaint.Status}")
    print(f"   Category: {complaint.CategoryType}")
    print(f"   Description: {complaint.ComplaintDescription[:80]}...")
    
    print(f"\n🔍 Auto-Generation Conditions:")
    
    # Check condition 1
    marketing_approved = complaint.MarketingReview and complaint.MarketingReview.lower().strip() == "approved"
    print(f"   1️⃣  Marketing Approved: {marketing_approved}")
    print(f"       Value: '{complaint.MarketingReview}'")
    
    # Check condition 2
    plant_approved = complaint.PlantHeadReview and complaint.PlantHeadReview.lower().strip() == "approved"
    print(f"   2️⃣  Plant Head Approved: {plant_approved}")
    print(f"       Value: '{complaint.PlantHeadReview}'")
    
    # Check condition 3
    has_rca = complaint.RootCauseAnalysis and complaint.RootCauseAnalysis.strip()
    print(f"   3️⃣  RCA Exists: {has_rca}")
    if has_rca:
        print(f"       Value: {complaint.RootCauseAnalysis[:60]}...")
    
    # Check condition 4
    has_capa = complaint.CorrectivePreventiveAction and complaint.CorrectivePreventiveAction.strip()
    print(f"   4️⃣  CAPA Exists: {has_capa}")
    if has_capa:
        print(f"       Value: {complaint.CorrectivePreventiveAction[:60]}...")
    
    # Check condition 5
    has_solution = complaint.Solution and complaint.Solution.strip()
    print(f"   5️⃣  Solution Already Exists: {has_solution}")
    
    print(f"\n✅ All conditions met: {marketing_approved and plant_approved and has_rca and has_capa}")
    print(f"   Current solution: {complaint.Solution[:100] if complaint.Solution else 'NULL'}")
    
    db.close()

if __name__ == "__main__":
    test_complaint_generation()
