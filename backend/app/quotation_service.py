"""
Quotation generation service with PDF export capabilities.

Handles:
- Quotation creation with pricing history lookup
- PDF quotation generation
- Quotation status tracking
"""
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .models import QuotationMaster, InventoryMaster, ProductMaster, CustomerDetail
from .config import settings


def get_price_history(db: Session, product_id: str, limit: int = 3) -> List[Tuple[float, datetime]]:
    """
    Retrieve the last N selling prices for a product from inventory history.
    
    Returns list of (price, date) tuples, most recent first.
    """
    records = db.query(
        InventoryMaster.SellingPrice,
        InventoryMaster.ProducedDate
    ).filter(
        InventoryMaster.PID == product_id,
        InventoryMaster.Category == 'Sold',
        InventoryMaster.SellingPrice.isnot(None)
    ).order_by(desc(InventoryMaster.ProducedDate)).limit(limit).all()
    
    return records


def calculate_average_price(price_history: List[Tuple[float, datetime]]) -> Optional[float]:
    """Calculate average price from price history."""
    if not price_history:
        return None
    prices = [p[0] for p in price_history]
    return sum(prices) / len(prices)


def generate_quotation_number(db: Session) -> str:
    """Generate a unique quotation number in format: QT-YYYY-MM-###"""
    today = datetime.now()
    count = db.query(QuotationMaster).filter(
        QuotationMaster.CreatedDate >= today.replace(hour=0, minute=0, second=0, microsecond=0)
    ).count() + 1
    return f"QT-{today.year}-{today.month:02d}-{count:03d}"


def create_quotation(
    db: Session,
    customer_id: str,
    product_id: str,
    product_name: str,
    quantity_mt: float,
    created_by: str,
    validity_days: int = 7,
    notes: str = ""
) -> QuotationMaster:
    """
    Create a new quotation with pricing based on recent history.
    
    Process:
    1. Get last 2-3 selling prices for the product
    2. Calculate average price
    3. Create quotation record
    4. Generate PDF
    """
    # Get price history
    price_history = get_price_history(db, product_id, limit=3)
    avg_price = calculate_average_price(price_history)
    
    # If no history, use the last produced item's initial price
    if not price_history:
        latest_inventory = db.query(InventoryMaster).filter(
            InventoryMaster.PID == product_id,
            InventoryMaster.Category == 'Produced'
        ).order_by(desc(InventoryMaster.ProducedDate)).first()
        
        if latest_inventory and latest_inventory.InitialPrice:
            avg_price = float(latest_inventory.InitialPrice)
        else:
            avg_price = 0.0
    
    # Calculate total amount (ensure both are floats)
    total_amount = float(quantity_mt) * float(avg_price)
    
    # Generate quotation number
    quotation_number = generate_quotation_number(db)
    
    # Create quotation record
    now = datetime.now()
    expiry_date = now + timedelta(days=validity_days)
    
    quotation = QuotationMaster(
        QuotationNumber=quotation_number,
        CID=customer_id,
        PID=product_id,
        ProductName=product_name,
        QuantityMT=quantity_mt,
        PricePerMT=avg_price,
        TotalAmount=total_amount,
        ValidityDays=validity_days,
        Notes=notes,
        Status='Generated',
        CreatedBy=created_by,
        CreatedDate=now,
        ExpiryDate=expiry_date
    )
    
    db.add(quotation)
    db.flush()  # Get the ID without committing
    
    # Generate PDF
    pdf_bytes = generate_quotation_pdf(
        quotation_id=quotation.QuotationID,
        quotation_number=quotation_number,
        customer_id=customer_id,
        product_name=product_name,
        quantity_mt=quantity_mt,
        price_per_mt=avg_price,
        total_amount=total_amount,
        price_history=price_history,
        validity_days=validity_days,
        notes=notes,
        db=db
    )
    
    # Save PDF to file
    pdf_path = save_quotation_pdf(pdf_bytes, quotation_number)
    quotation.PDFFilePath = str(pdf_path)
    
    db.add(quotation)
    db.commit()
    
    return quotation


def generate_quotation_pdf(
    quotation_id: int,
    quotation_number: str,
    customer_id: str,
    product_name: str,
    quantity_mt: float,
    price_per_mt: float,
    total_amount: float,
    price_history: List[Tuple[float, datetime]],
    validity_days: int,
    notes: str,
    db: Session
) -> bytes:
    """Generate a professional PDF quotation."""
    
    # Get customer details
    customer = db.query(CustomerDetail).filter(CustomerDetail.CID == customer_id).first()
    
    # Create PDF in memory
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Build story (content)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4
    )
    
    # Header
    story.append(Paragraph("QUOTATION", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Quotation Details
    header_data = [
        ['Quotation Number:', quotation_number],
        ['Date:', datetime.now().strftime('%d-%m-%Y')],
        ['Valid Till:', (datetime.now() + timedelta(days=validity_days)).strftime('%d-%m-%Y')],
        ['Validity:', f'{validity_days} days']
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Customer Details
    if customer:
        story.append(Paragraph("BILL TO:", heading_style))
        customer_info = [
            f"<b>Company:</b> {customer.CustomerName or 'N/A'}",
            f"<b>Contact Person:</b> {customer.ContactPerson or 'N/A'}",
            f"<b>Email:</b> {customer.Email or 'N/A'}",
            f"<b>Mobile:</b> {customer.Mobile or 'N/A'}",
            f"<b>Address:</b> {customer.City or ''}, {customer.State or ''} {customer.PostalCode or ''}",
        ]
        for info in customer_info:
            story.append(Paragraph(info, normal_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Product Details
    story.append(Paragraph("QUOTATION DETAILS:", heading_style))
    
    product_data = [
        ['Description', 'Quantity (MT)', 'Unit Price (INR/MT)', 'Amount (INR)'],
        [product_name, f'{quantity_mt:,.2f}', f'{price_per_mt:,.2f}', f'{total_amount:,.2f}']
    ]
    
    product_table = Table(product_data, colWidths=[3*inch, 1.2*inch, 1.3*inch, 1.3*inch])
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
    ]))
    story.append(product_table)
    story.append(Spacer(1, 0.1*inch))
    
    # Totals
    totals_data = [
        ['', '', 'TOTAL AMOUNT:', f'₹ {total_amount:,.2f}']
    ]
    totals_table = Table(totals_data, colWidths=[3*inch, 1.2*inch, 1.3*inch, 1.3*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, 0), (3, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (3, 0), 12),
        ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#e8eaf6')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Price History
    if price_history:
        story.append(Paragraph("PRICING HISTORY (Last 2-3 Sales):", heading_style))
        history_data = [['Date', 'Price per MT (INR)']]
        for price, date in price_history:
            history_data.append([
                date.strftime('%d-%m-%Y') if isinstance(date, datetime) else str(date),
                f'{price:,.2f}'
            ])
        
        history_table = Table(history_data, colWidths=[3*inch, 3*inch])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        story.append(history_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Notes/Terms
    if notes:
        story.append(Paragraph("NOTES & TERMS:", heading_style))
        story.append(Paragraph(notes, normal_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Footer
    footer_text = (
        f"This quotation is valid for {validity_days} days from the date of issue. "
        "Final pricing is subject to inventory availability and market conditions. "
        "For further assistance, please contact our sales team."
    )
    story.append(Paragraph(footer_text, normal_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Thank you for your interest in our products!", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def save_quotation_pdf(pdf_bytes: bytes, quotation_number: str) -> Path:
    """Save PDF to file system."""
    # Create quotations directory if it doesn't exist
    quotations_dir = Path("quotations")
    quotations_dir.mkdir(exist_ok=True)
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{quotation_number}_{timestamp}.pdf"
    filepath = quotations_dir / filename
    
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)
    
    return filepath


def format_quotation_text(
    quotation_number: str,
    product_name: str,
    quantity_mt: float,
    price_per_mt: float,
    total_amount: float,
    price_history: List[Tuple[float, datetime]],
    validity_days: int
) -> str:
    """Generate a formatted text quotation for chat display (without price shown to customer)."""
    
    quotation_text = f"""
**QUOTATION GENERATED**

Quotation Number: **{quotation_number}**
Generated Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}
Valid Till: {(datetime.now() + timedelta(days=validity_days)).strftime('%d-%m-%Y')}
Validity: {validity_days} days

**PRODUCT DETAILS:**
Product: {product_name}
Quantity: {quantity_mt:,.2f} MT

**QUOTATION DOCUMENT:**
A detailed PDF quotation has been generated and is attached. You can download it for your records and review the complete pricing details.

**NEXT STEPS:**
Please review this quotation and let us know if you have any questions. 
Our sales team will contact you shortly to confirm your order or discuss any modifications.

Thank you!
""".strip()
    
    return quotation_text
