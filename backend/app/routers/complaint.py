from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ComplaintMaster, LoginMaster
from ..schemas import ComplaintIn, ComplaintOut, ComplaintReviewIn, ComplaintSolutionGenerateIn
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


def generate_solution_with_approvals(
    complaint: ComplaintMaster,
    root_cause_analysis: str,
    corrective_preventive_action: str,
    marketing_head_review: Optional[str] = None,
    plant_head_review: Optional[str] = None
):
    """
    Generate solution if both marketing head and plant head have reviews.
    Solution is based on:
    - Root cause analysis
    - Corrective/preventive action
    - Marketing head review (any remarks/comments)
    - Plant head review (any remarks/comments)
    
    Both fields must have content (implicit approval if non-empty)
    They can contain:
    - Just "approved"
    - "approved - remarks"
    - Just remarks (implicit approval)
    """
    
    # Check if both have reviews
    has_marketing_review = marketing_head_review and marketing_head_review.strip()
    has_plant_review = plant_head_review and plant_head_review.strip()
    
    if not has_marketing_review or not has_plant_review:
        return None, "Both Marketing Head and Plant Head must provide reviews before solution can be generated."
    
    # Build the prompt with all inputs including reviews
    verified_data = f"""Complaint Analysis:
- Category: {complaint.CategoryType or 'General'}
- Description: {complaint.ComplaintDescription}
- PO Number: {complaint.PONumber or 'Not provided'}
- Dispatch Date: {complaint.DispatchDate or 'Not provided'}

Root Cause Analysis:
{root_cause_analysis}

Corrective and Preventive Action:
{corrective_preventive_action}"""
    
    # Add marketing head review/remarks
    if has_marketing_review:
        marketing_review_text = marketing_head_review.strip()
        # Remove "approved" prefix if it exists to get just the remarks
        if marketing_review_text.lower().startswith("approved"):
            # Remove "approved" and the separator
            remarks = marketing_review_text[8:].strip()  # Remove "approved"
            if remarks.startswith("-"):
                remarks = remarks[1:].strip()  # Remove "-" separator
            if remarks:
                verified_data += f"""

Marketing Head Review:
{remarks}"""
        else:
            # Just remarks, no "approved" prefix
            verified_data += f"""

Marketing Head Review:
{marketing_review_text}"""
    
    # Add plant head review/remarks
    if has_plant_review:
        plant_review_text = plant_head_review.strip()
        # Remove "approved" prefix if it exists to get just the remarks
        if plant_review_text.lower().startswith("approved"):
            # Remove "approved" and the separator
            remarks = plant_review_text[8:].strip()  # Remove "approved"
            if remarks.startswith("-"):
                remarks = remarks[1:].strip()  # Remove "-" separator
            if remarks:
                verified_data += f"""

Plant Head Review:
{remarks}"""
        else:
            # Just remarks, no "approved" prefix
            verified_data += f"""

Plant Head Review:
{plant_review_text}"""
    
    verified_data += "\n\nPlease generate the final solution based on the above analysis, actions, and reviews."
    
    prompt = """Based on the root cause analysis, corrective/preventive actions, and the reviews from marketing head and plant head, 
generate a comprehensive solution that addresses the complaint. 
Provide 3-4 sentences with clear, actionable steps that incorporate insights from all stakeholders and any remarks provided.

Format as:
SOLUTION: [your solution]"""
    
    response = generate_reply(prompt, verified_data)
    
    # Default fallback - use provided data to construct solution
    solution = f"Based on the root cause analysis: {root_cause_analysis[:80]}... The corrective action will include: {corrective_preventive_action[:80]}..."
    
    # Parse the response if we got one from Ollama
    if response:
        try:
            if "SOLUTION:" in response:
                solution = response.split("SOLUTION:")[1].strip()
            else:
                # If Ollama returned something without SOLUTION: prefix, use it as is
                solution = response.strip()
        except Exception:
            pass
    
    return solution, None


def regenerate_solution_if_conditions_met(complaint: ComplaintMaster):
    """
    Helper function to regenerate solution if all conditions are met:
    - Both Marketing and Plant Head have reviews (with or without "approved")
    - RCA and CAPA exist
    
    Note: Both Marketing and Plant Head fields must have SOME value (not null/empty)
    They can be:
    - "approved"
    - "approved - remarks"
    - Just remarks (implicit approval)
    """
    # Check if both have reviews (implicit or explicit approval)
    has_marketing_review = complaint.MarketingReview and complaint.MarketingReview.strip()
    has_plant_review = complaint.PlantHeadReview and complaint.PlantHeadReview.strip()
    
    has_rca = complaint.RootCauseAnalysis and complaint.RootCauseAnalysis.strip()
    has_capa = complaint.CorrectivePreventiveAction and complaint.CorrectivePreventiveAction.strip()
    
    if has_marketing_review and has_plant_review and has_rca and has_capa:
        solution, error = generate_solution_with_approvals(
            complaint,
            complaint.RootCauseAnalysis,
            complaint.CorrectivePreventiveAction,
            marketing_head_review=complaint.MarketingReview,
            plant_head_review=complaint.PlantHeadReview
        )
        
        if not error:
            complaint.Solution = solution
            complaint.Status = "Resolved"
            return True
    return False


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(
    complaint_id: str,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get complaint details by ID."""
    complaint = db.query(ComplaintMaster).filter(
        ComplaintMaster.ComplaintID == complaint_id
    ).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return ComplaintOut.from_orm(complaint)


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
    
    # Get count of complaints today to ensure uniqueness
    today_complaints = db.query(ComplaintMaster).filter(
        ComplaintMaster.CreatedDate >= today.replace(hour=0, minute=0, second=0)
    ).count()
    
    complaint_id = f"CMP-{today_str}-{today_complaints + 1:04d}"
    
    # Create complaint record
    complaint = ComplaintMaster(
        ComplaintID=complaint_id,
        CategoryType=payload.category_type or "General",
        ComplaintDescription=payload.description,
        PONumber=payload.po_number,
        DispatchDate=datetime.strptime(payload.dispatch_date, "%Y-%m-%d").date() if payload.dispatch_date else None,
        Status="Under Review",
        CreatedBy=user_id,
        CreatedDate=datetime.now(),
    )
    
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    
    return ComplaintOut.from_orm(complaint)


@router.post("/review", response_model=ComplaintOut)
def submit_complaint_review(
    payload: ComplaintReviewIn,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit a review for a complaint (marketing head, plant head, or HOD).
    Supports both "approved" and "approved - remarks" format.
    If both Marketing and Plant Head have approval, solution is auto-generated.
    """
    complaint = db.query(ComplaintMaster).filter(
        ComplaintMaster.ComplaintID == payload.complaint_id
    ).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    review_type = payload.review_type.lower()
    
    # Format the review value:
    # If only approval_status, use it
    # If comments provided with "approved" status, combine them
    if payload.approval_status.lower().strip() == "approved":
        if payload.review_comments:
            review_value = f"approved - {payload.review_comments}"
        else:
            review_value = "approved"
    else:
        review_value = payload.review_comments if payload.review_comments else payload.approval_status.lower()
    
    if review_type == "marketing":
        complaint.MarketingReview = review_value
        complaint.MarketingReviewDate = datetime.now()
    elif review_type == "plant_head":
        complaint.PlantHeadReview = review_value
        complaint.PlantHeadReviewDate = datetime.now()
    elif review_type == "hod":
        complaint.HODReview = review_value
        complaint.HODReviewDate = datetime.now()
    else:
        raise HTTPException(status_code=400, detail="Invalid review_type. Use 'marketing', 'plant_head', or 'hod'")
    
    complaint.UpdatedBy = current_user.User_Id
    complaint.UpdatedDate = datetime.now()
    
    # Auto-generate solution if conditions met
    regenerate_solution_if_conditions_met(complaint)
    
    db.commit()
    db.refresh(complaint)
    
    return ComplaintOut.from_orm(complaint)


@router.put("/review/{complaint_id}", response_model=ComplaintOut)
def update_complaint_review(
    complaint_id: str,
    payload: ComplaintReviewIn,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update/Edit an existing review for a complaint.
    Supports both "approved" and "approved - remarks" format.
    This will also trigger auto-generation if conditions are met.
    """
    complaint = db.query(ComplaintMaster).filter(
        ComplaintMaster.ComplaintID == complaint_id
    ).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    review_type = payload.review_type.lower()
    
    # Format the review value:
    # If only approval_status, use it
    # If comments provided with "approved" status, combine them
    if payload.approval_status.lower().strip() == "approved":
        if payload.review_comments:
            review_value = f"approved - {payload.review_comments}"
        else:
            review_value = "approved"
    else:
        review_value = payload.review_comments if payload.review_comments else payload.approval_status.lower()
    
    if review_type == "marketing":
        complaint.MarketingReview = review_value
        complaint.MarketingReviewDate = datetime.now()
    elif review_type == "plant_head":
        complaint.PlantHeadReview = review_value
        complaint.PlantHeadReviewDate = datetime.now()
    elif review_type == "hod":
        complaint.HODReview = review_value
        complaint.HODReviewDate = datetime.now()
    else:
        raise HTTPException(status_code=400, detail="Invalid review_type. Use 'marketing', 'plant_head', or 'hod'")
    
    complaint.UpdatedBy = current_user.User_Id
    complaint.UpdatedDate = datetime.now()
    
    # Regenerate solution if conditions met
    regenerate_solution_if_conditions_met(complaint)
    
    db.commit()
    db.refresh(complaint)
    
    return ComplaintOut.from_orm(complaint)


@router.post("/{complaint_id}/trigger-solution", response_model=ComplaintOut)
def trigger_solution_generation(
    complaint_id: str,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually trigger solution generation for testing/debugging.
    Useful when you want to regenerate solution with existing data.
    Both Marketing Head and Plant Head must have reviews (with or without "approved" text).
    """
    complaint = db.query(ComplaintMaster).filter(
        ComplaintMaster.ComplaintID == complaint_id
    ).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Try to regenerate solution with current data
    success = regenerate_solution_if_conditions_met(complaint)
    
    if not success:
        # Return what conditions are missing
        has_marketing_review = complaint.MarketingReview and complaint.MarketingReview.strip()
        has_plant_review = complaint.PlantHeadReview and complaint.PlantHeadReview.strip()
        has_rca = complaint.RootCauseAnalysis and complaint.RootCauseAnalysis.strip()
        has_capa = complaint.CorrectivePreventiveAction and complaint.CorrectivePreventiveAction.strip()
        
        missing = []
        if not has_marketing_review:
            missing.append("Marketing Head Review")
        if not has_plant_review:
            missing.append("Plant Head Review")
        if not has_rca:
            missing.append("Root Cause Analysis")
        if not has_capa:
            missing.append("Corrective/Preventive Action")
        
        raise HTTPException(
            status_code=400,
            detail=f"Cannot generate solution. Missing: {', '.join(missing)}"
        )
    
    complaint.UpdatedBy = current_user.User_Id
    complaint.UpdatedDate = datetime.now()
    
    db.commit()
    db.refresh(complaint)
    
    return ComplaintOut.from_orm(complaint)


@router.post("/regenerate-all-solutions", response_model=dict)
def regenerate_all_solutions(
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Regenerate solutions for ALL complaints that meet criteria:
    - Both Marketing and Plant Head approved
    - RCA and CAPA exist
    - No solution yet
    
    This is useful after updating the database directly with MSSQL.
    Call this endpoint to regenerate solutions for all edited complaints.
    """
    # Find all complaints that meet criteria
    complaints = db.query(ComplaintMaster).filter(
        ComplaintMaster.MarketingReview.ilike('approved'),
        ComplaintMaster.PlantHeadReview.ilike('approved'),
        ComplaintMaster.RootCauseAnalysis != None,
        ComplaintMaster.RootCauseAnalysis != '',
        ComplaintMaster.CorrectivePreventiveAction != None,
        ComplaintMaster.CorrectivePreventiveAction != '',
        (ComplaintMaster.Solution == None) | (ComplaintMaster.Solution == '')
    ).all()
    
    regenerated_count = 0
    failed_complaints = []
    
    for complaint in complaints:
        try:
            success = regenerate_solution_if_conditions_met(complaint)
            if success:
                regenerated_count += 1
            else:
                failed_complaints.append(complaint.ComplaintID)
        except Exception as e:
            failed_complaints.append(f"{complaint.ComplaintID}: {str(e)}")
    
    # Commit all changes
    db.commit()
    
    return {
        "message": "Solution regeneration completed",
        "total_found": len(complaints),
        "regenerated": regenerated_count,
        "failed": len(failed_complaints),
        "failed_complaints": failed_complaints
    }


@router.post("/generate-solution", response_model=ComplaintOut)
def generate_complaint_solution(
    payload: ComplaintSolutionGenerateIn,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate solution for a complaint.
    Only works if both Marketing Head and Plant Head have approved (status='approved').
    Solution is based on:
    - Root cause analysis
    - Corrective/preventive action
    - Marketing Head review
    - Plant Head review
    
    The approval information is NOT included in the final solution.
    """
    complaint = db.query(ComplaintMaster).filter(
        ComplaintMaster.ComplaintID == payload.complaint_id
    ).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Check if both marketing head and plant head approved
    marketing_approved = complaint.MarketingReview and complaint.MarketingReview.lower().strip() == "approved"
    plant_approved = complaint.PlantHeadReview and complaint.PlantHeadReview.lower().strip() == "approved"
    
    if not marketing_approved:
        raise HTTPException(
            status_code=400,
            detail="Marketing Head approval required. Current status: " + (complaint.MarketingReview or "pending")
        )
    
    if not plant_approved:
        raise HTTPException(
            status_code=400,
            detail="Plant Head approval required. Current status: " + (complaint.PlantHeadReview or "pending")
        )
    
    # Store RCA and CAPA
    complaint.RootCauseAnalysis = payload.root_cause_analysis
    complaint.RootCauseAnalysisDate = datetime.now()
    complaint.CorrectivePreventiveAction = payload.corrective_preventive_action
    complaint.CorrectivePreventiveActionDate = datetime.now()
    
    # Generate the solution
    solution, error = generate_solution_with_approvals(
        complaint,
        payload.root_cause_analysis,
        payload.corrective_preventive_action,
        marketing_head_review=complaint.MarketingReview,
        plant_head_review=complaint.PlantHeadReview
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # Update complaint with the generated solution
    complaint.Solution = solution
    complaint.Status = "Resolved"
    complaint.UpdatedBy = current_user.User_Id
    complaint.UpdatedDate = datetime.now()
    
    db.commit()
    db.refresh(complaint)
    
    return ComplaintOut.from_orm(complaint)


@router.put("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(
    complaint_id: str,
    payload: ComplaintIn,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update complaint details (category, description, PO number, dispatch date).
    If all solution conditions are met, solution will be regenerated.
    """
    complaint = db.query(ComplaintMaster).filter(
        ComplaintMaster.ComplaintID == complaint_id
    ).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Update fields if provided
    if payload.category_type:
        complaint.CategoryType = payload.category_type
    if payload.description:
        complaint.ComplaintDescription = payload.description
    if payload.po_number:
        complaint.PONumber = payload.po_number
    if payload.dispatch_date:
        complaint.DispatchDate = datetime.strptime(payload.dispatch_date, "%Y-%m-%d").date()
    
    complaint.UpdatedBy = current_user.User_Id
    complaint.UpdatedDate = datetime.now()
    
    # Regenerate solution if conditions met
    regenerate_solution_if_conditions_met(complaint)
    
    db.commit()
    db.refresh(complaint)
    
    return ComplaintOut.from_orm(complaint)


@router.put("/{complaint_id}/analysis", response_model=ComplaintOut)
def update_analysis(
    complaint_id: str,
    payload: ComplaintSolutionGenerateIn,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update Root Cause Analysis and Corrective/Preventive Action.
    If both Marketing Head and Plant Head have approved, solution will be auto-regenerated.
    """
    complaint = db.query(ComplaintMaster).filter(
        ComplaintMaster.ComplaintID == complaint_id
    ).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Update RCA and CAPA
    complaint.RootCauseAnalysis = payload.root_cause_analysis
    complaint.RootCauseAnalysisDate = datetime.now()
    complaint.CorrectivePreventiveAction = payload.corrective_preventive_action
    complaint.CorrectivePreventiveActionDate = datetime.now()
    complaint.UpdatedBy = current_user.User_Id
    complaint.UpdatedDate = datetime.now()
    
    # Auto-generate solution if conditions met
    regenerate_solution_if_conditions_met(complaint)
    
    db.commit()
    db.refresh(complaint)
    
    return ComplaintOut.from_orm(complaint)
