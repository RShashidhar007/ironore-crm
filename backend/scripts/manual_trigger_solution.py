"""
Manual trigger script - Call this to immediately regenerate all solutions
without needing the backend server or API calls.

Run: python scripts/manual_trigger_solution.py
"""
import sys
sys.path.insert(0, '/projects/ironore-crm/backend')

from app.database import SessionLocal
from app.models import ComplaintMaster
from app.routers.complaint import regenerate_solution_if_conditions_met

def manual_trigger_all_solutions():
    """Manually trigger solution generation for all ready complaints"""
    db = SessionLocal()
    
    try:
        # Get all complaints
        all_complaints = db.query(ComplaintMaster).all()
        
        # Filter in Python
        ready_complaints = []
        for c in all_complaints:
            has_marketing = c.MarketingReview and str(c.MarketingReview).strip()
            has_plant = c.PlantHeadReview and str(c.PlantHeadReview).strip()
            has_rca = c.RootCauseAnalysis and str(c.RootCauseAnalysis).strip()
            has_capa = c.CorrectivePreventiveAction and str(c.CorrectivePreventiveAction).strip()
            has_no_solution = not c.Solution or not str(c.Solution).strip()
            
            if has_marketing and has_plant and has_rca and has_capa and has_no_solution:
                ready_complaints.append(c)
        
        print("\n[Manual Solution Generation Trigger]")
        print("Found {} complaints ready for solution generation".format(len(ready_complaints)))
        
        regenerated_count = 0
        failed = []
        
        for complaint in ready_complaints:
            print("\nProcessing: {}".format(complaint.ComplaintID))
            print("  Marketing Review: {}...".format(complaint.MarketingReview[:50]))
            print("  Plant Head Review: {}...".format(complaint.PlantHeadReview[:50]))
            
            try:
                success = regenerate_solution_if_conditions_met(complaint)
                
                if success:
                    print("  Status: SUCCESS - Solution generated!")
                    print("  Solution: {}...".format(complaint.Solution[:80] if complaint.Solution else 'NULL'))
                    regenerated_count += 1
                else:
                    print("  Status: SKIPPED - Conditions not met")
                    failed.append(complaint.ComplaintID)
            
            except Exception as e:
                print("  Status: FAILED - {}".format(str(e)))
                failed.append(complaint.ComplaintID)
        
        # Commit all changes
        db.commit()
        
        print("\n[RESULTS]")
        print("Total found: {}".format(len(ready_complaints)))
        print("Generated: {}".format(regenerated_count))
        print("Failed: {}".format(len(failed)))
        if failed:
            print("Failed complaints: {}".format(failed))
        
    finally:
        db.close()

if __name__ == "__main__":
    manual_trigger_all_solutions()
