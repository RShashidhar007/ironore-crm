"""
Real-time monitor to watch solution generation updates
Run this script and it will show you whenever a solution is generated
"""
import sys
sys.path.insert(0, '/projects/ironore-crm/backend')

import time
from datetime import datetime
from app.database import SessionLocal
from app.models import ComplaintMaster

def monitor_solutions(complaint_id=None, check_interval=5):
    """
    Monitor solution generation in real-time
    
    Args:
        complaint_id: Specific complaint to monitor (or None for all)
        check_interval: How often to check (seconds)
    """
    db = SessionLocal()
    try:
        print("\n" + "="*80)
        print("SOLUTION GENERATION MONITOR")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Check interval: {check_interval} seconds")
        
        if complaint_id:
            print(f"Monitoring: {complaint_id}")
        else:
            print("Monitoring: ALL complaints")
        
        print("="*80)
        print("\nWatching for solution updates...\n")
        
        last_solutions = {}  # Track previous state
        
        while True:
            # Get current state
            if complaint_id:
                complaints = db.query(ComplaintMaster).filter(
                    ComplaintMaster.ComplaintID == complaint_id
                ).all()
            else:
                complaints = db.query(ComplaintMaster).all()
            
            for complaint in complaints:
                current_state = {
                    'id': complaint.ComplaintID,
                    'has_solution': bool(complaint.Solution and str(complaint.Solution).strip()),
                    'solution_length': len(str(complaint.Solution)) if complaint.Solution else 0,
                    'status': complaint.Status,
                    'updated': complaint.UpdatedDate
                }
                
                # Check if solution changed
                if complaint.ComplaintID in last_solutions:
                    prev_state = last_solutions[complaint.ComplaintID]
                    
                    # Solution was generated (went from no solution to has solution)
                    if not prev_state['has_solution'] and current_state['has_solution']:
                        print(f"\n{'='*80}")
                        print(f"SOLUTION GENERATED! {datetime.now().strftime('%H:%M:%S')}")
                        print(f"{'='*80}")
                        print(f"Complaint ID: {complaint.ComplaintID}")
                        print(f"Status: {complaint.Status}")
                        print(f"Updated: {complaint.UpdatedDate}")
                        print(f"Solution Preview: {str(complaint.Solution)[:150]}...")
                        print(f"Solution Length: {current_state['solution_length']} characters")
                        print(f"{'='*80}\n")
                    
                    # Solution was cleared (marked for regeneration)
                    elif prev_state['has_solution'] and not current_state['has_solution']:
                        print(f"\n{datetime.now().strftime('%H:%M:%S')} - Solution cleared for {complaint.ComplaintID}")
                        print(f"  Reason: Marked for regeneration")
                        print(f"  Status: {complaint.Status}\n")
                
                # Store current state
                last_solutions[complaint.ComplaintID] = current_state
            
            # Print current time (so you know it's still running)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking...", end='\r')
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Monitor specific complaint (or None to monitor all)
    monitor_complaint_id = None  # Change to 'CMP-20260825-0005' to monitor specific
    
    # Run monitor
    monitor_solutions(complaint_id=monitor_complaint_id, check_interval=5)
