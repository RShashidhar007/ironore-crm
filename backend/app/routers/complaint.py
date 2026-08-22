from datetime import datetime
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db
from ..models import ComplaintMaster, LoginMaster
from ..schemas import ComplaintIn, ComplaintOut
from ..auth import get_current_user
from ..ollama_client import generate_reply

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def generate_complaint_summary_and_solution(category: str, description: str, po_number: Optional[str] = None, dispatch_date: Optional[str] = None):
    """Generate AI summary and solution for the complaint."""
    
    # Build the verified data context - this is what Ollama will analyze
    verified_data = f"""Complaint Information from Customer:
- Product Category: {category or 'General'}
- Customer's Description: {description}
- PO Number: {po_number or 'Not provided'}
- Dispatch Date: {dispatch_date or 'Not provided'}

This is a complaint about iron ore or iron pellet products. Please analyze and provide guidance."""
    
    # Build the instruction prompt
    customer_message = """Analyze this complaint and provide:
1. SUMMARY: A brief 2-3 sentence summary of the customer's issue
2. SOLUTION: Recommended solution or next steps in 2-3 sentences

Format EXACTLY as:
SUMMARY: [your summary]
SOLUTION: [your solution]"""
    
    # Call Ollama
    response = generate_reply(customer_message, verified_data)
    
    # Default fallback values
    summary = f"Customer complaint regarding {category or 'product quality'}: {description[:150]}{'...' if len(description) > 150 else ''}"
    solution = "Our technical team is reviewing this issue and will provide an update within 24-48 hours."
    
    # Parse the response if we got one
    if response:
        try:
            if "SUMMARY:" in response and "SOLUTION:" in response:
                parts = response.split("SOLUTION:")
                summary = parts[0].replace("SUMMARY:", "").strip()
                solution = parts[1].strip()
        except Exception:
            # Keep fallback values
            pass
    
    return summary, solution


@router.post("", response_model=ComplaintOut)
def create_complaint(
    payload: ComplaintIn,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new complaint and return the complaint ID."""
    # Use the authenticated user's ID
    user_id = current_user.User_Id
    
    # Generate unique complaint ID
    today = datetime.now()
    today_str = today.strftime("%Y%m%d")
    
    # Get count of complaints today for this user to ensure uniqueness
    today_complaints = db.query(ComplaintMaster).filter(
        ComplaintMaster.CreatedDate >= today.replace(hour=0, minute=0, second=0)
    ).count()
    
    complaint_id = f"CMP-{today_str}-{today_complaints + 1:04d}"
    
    # Generate AI summary and solution
    summary, solution = generate_complaint_summary_and_solution(
        category=payload.category_type or "General",
        description=payload.description,
        po_number=payload.po_number,
        dispatch_date=payload.dispatch_date
    )
    
    # Create complaint record
    complaint = ComplaintMaster(
        ComplaintID=complaint_id,
        CategoryType=payload.category_type or "General",
        ComplaintDescription=payload.description,
        PONumber=payload.po_number,
        DispatchDate=datetime.strptime(payload.dispatch_date, "%Y-%m-%d").date() if payload.dispatch_date else None,
        Summary=summary,
        Solution=solution,
        Progress="Complaint registered and under initial review",
        Status="Under Review",
        CreatedBy=user_id,
        CreatedDate=datetime.now(),
    )
    
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    
    return ComplaintOut(
        ComplaintID=complaint.ComplaintID,
        CategoryType=complaint.CategoryType,
        ComplaintDescription=complaint.ComplaintDescription,
        PONumber=complaint.PONumber,
        DispatchDate=complaint.DispatchDate,
        Summary=complaint.Summary,
        Solution=complaint.Solution,
        Progress=complaint.Progress,
        Status=complaint.Status,
        CreatedBy=complaint.CreatedBy,
        CreatedDate=complaint.CreatedDate.date() if complaint.CreatedDate else None,
        UpdatedBy=complaint.UpdatedBy,
        UpdatedDate=complaint.UpdatedDate.date() if complaint.UpdatedDate else None,
    )
