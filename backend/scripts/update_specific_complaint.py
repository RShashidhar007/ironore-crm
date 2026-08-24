"""
Update a specific complaint with AI-generated summary and solution
"""
import sys
from datetime import datetime
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import ComplaintMaster
from update_complaint_summaries import generate_complaint_summary_and_solution

if len(sys.argv) < 2:
    print("Usage: python update_specific_complaint.py <complaint_id>")
    sys.exit(1)

complaint_id = sys.argv[1]

db = SessionLocal()

# Get the complaint
complaint = db.query(ComplaintMaster).filter(
    ComplaintMaster.ComplaintID == complaint_id
).first()

if not complaint:
    print(f"Complaint {complaint_id} not found")
    db.close()
    sys.exit(1)

print(f"Found Complaint: {complaint.ComplaintID}")
print(f"Category: {complaint.CategoryType}")
print(f"Description: {complaint.ComplaintDescription}")
print(f"Current Summary: {complaint.Summary}")
print(f"Current Solution: {complaint.Solution}")
print(f"Current Progress: {complaint.Progress}")
print(f"Current Status: {complaint.Status}")
print("\n" + "="*60)
print("Generating AI summary and solution...")
print("="*60 + "\n")

# Generate new summary and solution
summary, solution = generate_complaint_summary_and_solution(
    category=complaint.CategoryType or "General",
    description=complaint.ComplaintDescription or "No description provided",
    po_number=complaint.PONumber,
    dispatch_date=complaint.DispatchDate.strftime('%Y-%m-%d') if complaint.DispatchDate else None
)

print(f"New Summary:\n{summary}\n")
print(f"New Solution:\n{solution}\n")

# Update the complaint
complaint.Summary = summary
complaint.Solution = solution

if not complaint.Progress:
    complaint.Progress = "Complaint registered and under initial review"
    
if not complaint.Status:
    complaint.Status = "Under Review"

complaint.UpdatedDate = datetime.now()
complaint.UpdatedBy = "AI_System"

db.commit()
print("="*60)
print(f"✓ Successfully updated Complaint {complaint.ComplaintID}")
print("="*60)

db.close()
