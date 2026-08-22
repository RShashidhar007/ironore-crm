"""
Populate all workflow columns for a specific complaint
"""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import ComplaintMaster

complaint_id = "CMP-20260821-0004"
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
print(f"Description: {complaint.ComplaintDescription}\n")

# Fill in all 10 workflow columns
complaint.RootCauseAnalysis = (
    "Investigation revealed that excessive sponge fines generation was caused by improper material handling during "
    "transportation and storage. The material was exposed to excessive vibration and moisture, which led to degradation "
    "of the pellet structure. Additionally, the storage temperature was not maintained within the specified range."
)
complaint.RootCauseAnalysisDate = datetime.now() - timedelta(days=3)

complaint.CorrectivePreventiveAction = (
    "We have implemented the following corrective actions: (1) Improved packaging with shock-absorbing materials, "
    "(2) Enhanced transportation protocols with temperature and humidity monitoring, (3) Upgraded storage facilities "
    "with climate control system, (4) Staff training on proper handling procedures. These measures will prevent similar "
    "issues in future shipments."
)
complaint.CorrectivePreventiveActionDate = datetime.now() - timedelta(days=2)

complaint.MarketingReview = "Approved - Solution is customer-friendly and maintains brand reputation"
complaint.MarketingReviewDate = datetime.now() - timedelta(days=1)

complaint.PlantHeadReview = "Approved - All corrective actions are technically sound and operationally feasible"
complaint.PlantHeadReviewDate = datetime.now() - timedelta(hours=12)

complaint.HODReview = "Approved - All procedures align with company standards and quality requirements"
complaint.HODReviewDate = datetime.now() - timedelta(hours=6)

# Save to database
db.commit()

print("="*80)
print("✅ Successfully populated all 10 workflow columns:")
print("="*80)
print(f"✓ RootCauseAnalysis: {complaint.RootCauseAnalysis[:80]}...")
print(f"✓ RootCauseAnalysisDate: {complaint.RootCauseAnalysisDate.strftime('%B %d, %Y')}")
print(f"\n✓ CorrectivePreventiveAction: {complaint.CorrectivePreventiveAction[:80]}...")
print(f"✓ CorrectivePreventiveActionDate: {complaint.CorrectivePreventiveActionDate.strftime('%B %d, %Y')}")
print(f"\n✓ MarketingReview: {complaint.MarketingReview}")
print(f"✓ MarketingReviewDate: {complaint.MarketingReviewDate.strftime('%B %d, %Y')}")
print(f"\n✓ PlantHeadReview: {complaint.PlantHeadReview}")
print(f"✓ PlantHeadReviewDate: {complaint.PlantHeadReviewDate.strftime('%B %d, %Y')}")
print(f"\n✓ HODReview: {complaint.HODReview}")
print(f"✓ HODReviewDate: {complaint.HODReviewDate.strftime('%B %d, %Y')}")
print("="*80)
print("\nNow when the customer checks this complaint, Ollama will:")
print("1. Analyze all 10 columns of data")
print("2. Generate a warm, human-friendly solution message")
print("3. Show it to the customer in the chat")
print("="*80)

db.close()
