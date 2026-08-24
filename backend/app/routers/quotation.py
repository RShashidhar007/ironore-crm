"""
Quotation generation and management API endpoints.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import QuotationMaster, ProductMaster, InventoryMaster
from ..auth import get_current_user, LoginMaster
from ..quotation_service import (
    create_quotation,
    get_price_history,
    calculate_average_price,
    format_quotation_text
)
from ..schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/quotations", tags=["quotations"])


class QuotationRequest:
    """Request model for quotation generation."""
    product_id: str
    quantity_mt: float
    notes: Optional[str] = None


@router.post("/generate")
def generate_quotation(
    product_id: str,
    quantity_mt: float,
    notes: Optional[str] = None,
    validity_days: int = 7,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new quotation for a customer.
    
    Process:
    1. Verify product exists and is available
    2. Get pricing history (last 2-3 sales)
    3. Calculate average price
    4. Create quotation record
    5. Generate PDF
    6. Return quotation details + PDF file
    """
    
    # Verify product exists
    product = db.query(ProductMaster).filter(ProductMaster.PID == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify quantity is positive
    if quantity_mt <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    # Get customer ID from login user
    customer_id = current_user.CID
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID not found for user")
    
    try:
        # Create quotation with pricing
        quotation = create_quotation(
            db=db,
            customer_id=customer_id,
            product_id=product_id,
            product_name=product.ProductName,
            quantity_mt=quantity_mt,
            created_by=current_user.User_Id,
            validity_days=validity_days,
            notes=notes or ""
        )
        
        # Get price history for display
        price_history = get_price_history(db, product_id, limit=3)
        
        # Format text response
        quotation_text = format_quotation_text(
            quotation_number=quotation.QuotationNumber,
            product_name=product.ProductName,
            quantity_mt=quantity_mt,
            price_per_mt=quotation.PricePerMT,
            total_amount=quotation.TotalAmount,
            price_history=price_history,
            validity_days=validity_days
        )
        
        return ChatResponse(
            reply=quotation_text,
            action_buttons=["Download PDF", "View Details", "Modify Quotation"],
            structured_data={
                "quotation_id": quotation.QuotationID,
                "quotation_number": quotation.QuotationNumber,
                "product_id": product_id,
                "quantity_mt": quantity_mt,
                "price_per_mt": quotation.PricePerMT,
                "total_amount": quotation.TotalAmount,
                "pdf_path": quotation.PDFFilePath,
                "validity_days": validity_days,
                "expiry_date": quotation.ExpiryDate.isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quotation: {str(e)}")


@router.get("/{quotation_id}")
def get_quotation(
    quotation_id: int,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve quotation details."""
    quotation = db.query(QuotationMaster).filter(QuotationMaster.QuotationID == quotation_id).first()
    
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Verify user has access to this quotation
    if quotation.CID != current_user.CID:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "quotation_id": quotation.QuotationID,
        "quotation_number": quotation.QuotationNumber,
        "product_name": quotation.ProductName,
        "quantity_mt": quotation.QuantityMT,
        "price_per_mt": quotation.PricePerMT,
        "total_amount": quotation.TotalAmount,
        "status": quotation.Status,
        "created_date": quotation.CreatedDate.isoformat(),
        "expiry_date": quotation.ExpiryDate.isoformat(),
        "pdf_path": quotation.PDFFilePath
    }


@router.get("/{quotation_id}/pdf")
def download_quotation_pdf(
    quotation_id: int,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download quotation PDF."""
    from fastapi.responses import FileResponse
    from pathlib import Path
    
    quotation = db.query(QuotationMaster).filter(QuotationMaster.QuotationID == quotation_id).first()
    
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Verify user has access
    if quotation.CID != current_user.CID:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not quotation.PDFFilePath or not Path(quotation.PDFFilePath).exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(
        quotation.PDFFilePath,
        filename=f"{quotation.QuotationNumber}.pdf",
        media_type="application/pdf"
    )


@router.get("")
def list_quotations(
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all quotations for current customer."""
    quotations = db.query(QuotationMaster).filter(
        QuotationMaster.CID == current_user.CID
    ).order_by(QuotationMaster.CreatedDate.desc()).all()
    
    return {
        "quotations": [
            {
                "quotation_id": q.QuotationID,
                "quotation_number": q.QuotationNumber,
                "product_name": q.ProductName,
                "quantity_mt": q.QuantityMT,
                "total_amount": q.TotalAmount,
                "status": q.Status,
                "created_date": q.CreatedDate.isoformat(),
                "expiry_date": q.ExpiryDate.isoformat()
            }
            for q in quotations
        ]
    }
