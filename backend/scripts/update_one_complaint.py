"""
Update one specific complaint to test AI generation
"""
import sys
from datetime import datetime
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import ComplaintMaster
from update_complaint_summaries import generate_complaint_summary_and_solution

db = SessionLocal()

# Get the first complaint
complaint = db.query(ComplaintMaster).first()

if not complaint:
    print("No complaints found in database")
    exit(1)

print(f"Testing AI generation for complaint: {complaint.ComplaintID}")
print(f"Category: {complaint.CategoryType}")
print(f"Description: {complaint.ComplaintDescription}\n")

# Generate new summary and solution
summary, solution = generate_complaint_summary_and_solution(
    category=complaint.CategoryType,
    description=complaint.ComplaintDescription or "No description",
    po_number=complaint.PONumber,
    dispatch_date=complaint.DispatchDate.strftime('%Y-%m-%d') if complaint.DispatchDate else None
)

print("="*60)
print("AI Generated Content:")
print("="*60)
print(f"\nSummary:\n{summary}\n")
print(f"\nSolution:\n{solution}\n")

# Update the complaint
complaint.Summary = summary
complaint.Solution = solution
complaint.UpdatedDate = datetime.now()
complaint.UpdatedBy = "AI_System"

db.commit()
print("✓ Complaint updated successfully!")
db.close()
