"""
Diagnostic script to check if solution generation system is working
Run this to see what's wrong
"""
import sys
sys.path.insert(0, '/projects/ironore-crm/backend')

from datetime import datetime
from app.database import SessionLocal
from app.models import ComplaintMaster

def diagnose():
    """Run diagnostic checks"""
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("SOLUTION GENERATION DIAGNOSTIC")
    print("="*80 + "\n")
    
    try:
        # Check 1: Database connection
        print("[1] Database Connection: ", end="")
        complaints = db.query(ComplaintMaster).count()
        print(f"OK - Found {complaints} complaints\n")
        
        # Check 2: Complaints with all 4 fields filled but no solution
        print("[2] Complaints Ready for Generation:")
        ready = db.query(ComplaintMaster).filter(
            ComplaintMaster.MarketingReview != None,
            ComplaintMaster.MarketingReview != '',
            ComplaintMaster.PlantHeadReview != None,
            ComplaintMaster.PlantHeadReview != '',
            ComplaintMaster.RootCauseAnalysis != None,
            ComplaintMaster.RootCauseAnalysis != '',
            ComplaintMaster.CorrectivePreventiveAction != None,
            ComplaintMaster.CorrectivePreventiveAction != '',
            (ComplaintMaster.Solution == None) | (ComplaintMaster.Solution == '')
        ).all()
        
        if ready:
            print(f"    Found {len(ready)} complaint(s) ready for generation:\n")
            for c in ready:
                print(f"    - {c.ComplaintID}")
                print(f"      Marketing: {str(c.MarketingReview)[:50]}...")
                print(f"      Plant: {str(c.PlantHeadReview)[:50]}...")
                print(f"      Status: {c.Status}\n")
        else:
            print("    NONE - All complaints with 4 fields filled already have solutions\n")
        
        # Check 3: Recently edited complaints
        print("[3] Recently Edited Complaints (Last 10 minutes):")
        from datetime import timedelta
        recent_time = datetime.now() - timedelta(minutes=10)
        recent = db.query(ComplaintMaster).filter(
            ComplaintMaster.UpdatedDate >= recent_time
        ).order_by(ComplaintMaster.UpdatedDate.desc()).all()
        
        if recent:
            print(f"    Found {len(recent)} recently edited:\n")
            for c in recent:
                has_all_fields = (
                    c.MarketingReview and str(c.MarketingReview).strip() and
                    c.PlantHeadReview and str(c.PlantHeadReview).strip() and
                    c.RootCauseAnalysis and str(c.RootCauseAnalysis).strip() and
                    c.CorrectivePreventiveAction and str(c.CorrectivePreventiveAction).strip()
                )
                has_solution = c.Solution and str(c.Solution).strip()
                
                print(f"    - {c.ComplaintID} (Updated: {c.UpdatedDate})")
                print(f"      All 4 fields: {'YES' if has_all_fields else 'NO'}")
                print(f"      Has Solution: {'YES' if has_solution else 'NO'}")
                print(f"      Status: {c.Status}\n")
        else:
            print("    NONE - No complaints edited in last 10 minutes\n")
        
        # Check 4: Check trigger log table exists
        print("[4] Trigger Log Table: ", end="")
        try:
            log_count = db.query(ComplaintMaster).count()  # Simple check
            print("EXISTS (checking for entries...)\n")
            
            # Try to see recent logs
            from sqlalchemy import text
            try:
                logs = db.query(text("SELECT TOP 5 * FROM SolutionGenerationLog ORDER BY CreatedAt DESC")).all()
                print(f"    Recent Trigger Events:\n")
                if logs:
                    for log in logs:
                        print(f"    - {log[2]}: {log[3][:60]}...\n")
                else:
                    print("    NO TRIGGER EVENTS LOGGED YET\n")
            except Exception as e:
                print(f"    (Log table might not exist yet: {str(e)[:50]})\n")
        except:
            print("DOES NOT EXIST\n")
        
        # Check 5: Solution field data
        print("[5] Solution Field Status:")
        with_solution = db.query(ComplaintMaster).filter(
            ComplaintMaster.Solution != None,
            ComplaintMaster.Solution != ''
        ).count()
        without_solution = db.query(ComplaintMaster).filter(
            (ComplaintMaster.Solution == None) |
            (ComplaintMaster.Solution == '')
        ).count()
        
        print(f"    With solutions: {with_solution}")
        print(f"    Without solutions: {without_solution}")
        print(f"    Total: {with_solution + without_solution}\n")
        
        # Check 6: Most recently updated complaint
        print("[6] Most Recently Updated Complaint:")
        latest = db.query(ComplaintMaster).order_by(
            ComplaintMaster.UpdatedDate.desc()
        ).first()
        
        if latest:
            print(f"    ID: {latest.ComplaintID}")
            print(f"    Updated: {latest.UpdatedDate}")
            print(f"    Marketing: {'YES' if latest.MarketingReview and str(latest.MarketingReview).strip() else 'NO'}")
            print(f"    Plant: {'YES' if latest.PlantHeadReview and str(latest.PlantHeadReview).strip() else 'NO'}")
            print(f"    RCA: {'YES' if latest.RootCauseAnalysis and str(latest.RootCauseAnalysis).strip() else 'NO'}")
            print(f"    CAPA: {'YES' if latest.CorrectivePreventiveAction and str(latest.CorrectivePreventiveAction).strip() else 'NO'}")
            print(f"    Solution: {'YES' if latest.Solution and str(latest.Solution).strip() else 'NO'}\n")
        
        # Check 7: Troubleshooting recommendations
        print("[7] Troubleshooting Checklist:")
        print("    [1] Is backend server running?")
        print("      python -m uvicorn app.main:app --reload")
        print()
        print("    [2] Is the trigger installed in MSSQL?")
        print("      Run: backend/database/instant_solution_trigger.sql")
        print()
        print("    [3] Did you click 'Update' (Ctrl+Enter) after editing?")
        print("      Just closing the Edit window doesn't trigger the update")
        print()
        print("    [4] Are ALL 4 fields filled?")
        print("      - MarketingReview: NOT NULL and NOT EMPTY")
        print("      - PlantHeadReview: NOT NULL and NOT EMPTY")
        print("      - RootCauseAnalysis: NOT NULL and NOT EMPTY")
        print("      - CorrectivePreventiveAction: NOT NULL and NOT EMPTY")
        print()
        print("    [5] Did you wait 30+ seconds for scheduler?")
        print("      Solution generates within 30 seconds after edit")
        print()
        print("    [6] Check the logs:")
        print("      SELECT * FROM SolutionGenerationLog ORDER BY CreatedAt DESC;")
        print()
        
        print("="*80 + "\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
