import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from ..database import get_db
from ..models import (
    CustomerDetail,
    ProductMaster,
    ProductCategoryMaster,
    IronOreSpecificationMaster,
    IronPelletSpecificationMaster,
    ComplaintMaster,
    LoginMaster,
    InventoryMaster,
)
from ..schemas import ChatRequest, ChatResponse, ComplaintIn, ComplaintOut
from ..auth import get_current_user
from ..config import settings, get_company_email, get_company_phone, get_company_whatsapp
from .. import ollama_client
from ..intent import (
    Intent,
    classify_intent,
    extract_product_hint,
    extract_lot_hint,
    extract_parameter_hint,
    extract_complaint_id,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


def format_price_per_mt(price: Optional[int], currency: str = "INR") -> str:
    """Format a price with per MT unit. E.g., 4500 INR/MT"""
    if price is None:
        return "N/A"
    return f"{price:,} {currency}/MT"


ALL_ACTIONS = [
    "Ask for a Quotation",
    "Place an Order",
    "Product Information",
    "Raise a Complaint",
    "Track my Complaint",
    "Contact Company via Email",
]

# Maps the frontend's one-click action buttons straight to an intent,
# bypassing free-text classification entirely.
ACTION_TO_INTENT = {
    "Ask for a Quotation": Intent.QUOTATION_REQUEST,
    "Place an Order": Intent.ORDER_REQUEST,
    "Product Information": Intent.PRODUCT_INFORMATION,
    "Raise a Complaint": Intent.COMPLAINT,
    "Track my Complaint": Intent.COMPLAINT_TRACKING,
    "Connect to Company": Intent.WHATSAPP_CONTACT,
    "Contact Company via Email": Intent.WHATSAPP_CONTACT,
}


def _find_product(db: Session, hint: Optional[str]) -> Optional[ProductMaster]:
    if not hint:
        return None
    hint_norm = hint.strip()
    product = db.get(ProductMaster, hint_norm.upper())
    if product:
        return product
    return (
        db.query(ProductMaster)
        .filter(or_(ProductMaster.PID.ilike(hint_norm), ProductMaster.ProductName.ilike(f"%{hint_norm}%")))
        .first()
    )


def _get_product_category(db: Session, product: ProductMaster) -> Optional[str]:
    """Manually look up product category by ID (ProductCategory is stored as string int)."""
    if not product.ProductCategory:
        return None
    try:
        cat_id = int(product.ProductCategory)
        category = db.get(ProductCategoryMaster, cat_id)
        return category.ProductCategory if category else None
    except (ValueError, TypeError):
        return None


def _spec_table_markdown(rows, include_testing_standard: bool) -> str:
    if not rows:
        return "(no specification rows found)"
    
    # Build a clean, simple specification summary
    specs = []
    for r in rows:
        param = (r.Parameter or "").strip()
        spec = (r.Specification or "").strip()
        lot_no = (getattr(r, "LotNo", None) or "").strip()
        testing_std = (getattr(r, "TestingStandard", None) or "").strip() if include_testing_standard else ""
        
        if param and spec:
            if include_testing_standard and testing_std:
                specs.append(f"• {param}: {spec} (Testing Standard: {testing_std})")
            elif lot_no:
                specs.append(f"• {param}: {spec} (Lot: {lot_no})")
            else:
                specs.append(f"• {param}: {spec}")
    
    if not specs:
        return "(no specification rows found)"
    
    return "Specifications:\n" + "\n".join(specs)


def _sanitize_reply(reply: str, current_customer_cid: Optional[str], db: Session) -> str:
    """
    Defense-in-depth response validation: strips anything that looks
    like it might leak SQL, credentials, or another customer's CID,
    even though the prompt already instructs the LLM not to produce
    these. The LLM's own output is untrusted input at this boundary.
    """
    if not reply:
        return reply
    # Strip anything that looks like a SQL statement leaking through.
    reply = re.sub(r"(?is)\b(select|insert|update|delete)\b.*?;?", "[removed]", reply) \
        if re.search(r"(?is)\bselect\s+.*\bfrom\b", reply) else reply
    # Strip obvious credential-shaped strings.
    reply = re.sub(r"(?i)(password|pwd)\s*[:=]\s*\S+", "[redacted]", reply)

    # Block leakage of other customers' CIDs mentioned verbatim.
    other_cids = [c.CID for c in db.query(CustomerDetail.CID).all()
                  if current_customer_cid is None or c.CID != current_customer_cid]
    for cid in other_cids:
        if cid and cid in reply:
            reply = reply.replace(cid, "[restricted]")
    return reply


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = payload.message or ""

    # Check for dynamic action patterns first (view_complaint:, complaint_category:, etc.)
    if payload.action:
        if payload.action.startswith("view_complaint:"):
            intent = Intent.COMPLAINT_TRACKING
        elif payload.action.startswith("order_quantity:"):
            intent = Intent.ORDER_REQUEST
        elif payload.action in ACTION_TO_INTENT:
            intent = ACTION_TO_INTENT[payload.action]
        else:
            intent = classify_intent(message)
    else:
        intent = classify_intent(message)

    # Get user display name for notifications
    user_display = current_user.User_Name or current_user.User_Id

    # If we guessed a spec intent (or the message just names a product +
    # "specification"), resolve the actual product and let its real
    # category decide Ore vs Pellet — free text alone is ambiguous
    # (e.g. "Fe specification for P003" doesn't say "pellet" or "ore").
    if intent in (Intent.IRON_ORE_SPECIFICATION, Intent.IRON_PELLET_SPECIFICATION):
        hint = extract_product_hint(message)
        product = _find_product(db, hint) if hint else None
        if product:
            cat_name = (_get_product_category(db, product) or "").lower()
            if "pellet" in cat_name:
                intent = Intent.IRON_PELLET_SPECIFICATION
            elif "ore" in cat_name:
                intent = Intent.IRON_ORE_SPECIFICATION

    verified_data = ""
    structured_data = None
    template_reply = None

    # ---------------- CUSTOMER_INFORMATION ----------------
    if intent == Intent.CUSTOMER_INFORMATION:
        customer = db.get(CustomerDetail, current_user.CID) if current_user.CID else None
        if not customer:
            verified_data = "No customer record is linked to this account."
            template_reply = "I couldn't find a customer record linked to your account. Please contact support."
        else:
            structured_data = {
                "customerCode": customer.CustomerCode,
                "customerName": customer.CustomerName,
                "contactPerson": customer.ContactPerson,
                "email": customer.Email,
                "mobile": customer.Mobile,
                "telephone": customer.Telephone,
                "gstNo": customer.GSTNo,
                "panNo": customer.PANNo,
                "address": ", ".join(filter(None, [customer.Street1, customer.Street2,
                                                     customer.Street3, customer.Street4,
                                                     customer.Location, customer.City,
                                                     customer.State, customer.PostalCode,
                                                     customer.Country])),
                "status": customer.Status,
            }
            verified_data = "\n".join(f"{k}: {v}" for k, v in structured_data.items())
            template_reply = (
                f"Here are your registered customer details:\n\n"
                f"- Customer Code: {customer.CustomerCode or 'not available'}\n"
                f"- Company: {customer.CustomerName or 'not available'}\n"
                f"- Contact Person: {customer.ContactPerson or 'not available'}\n"
                f"- Email: {customer.Email or 'not available'}\n"
                f"- Mobile: {customer.Mobile or 'not available'}\n"
                f"- GST No.: {customer.GSTNo or 'not available'}\n"
                f"- Registered Address: {structured_data['address'] or 'not available'}"
            )

    # ---------------- PRODUCT_CATEGORY ----------------
    elif intent == Intent.PRODUCT_CATEGORY:
        cats = db.query(ProductCategoryMaster).filter(ProductCategoryMaster.PStatus == 1).all()
        structured_data = [{"id": c.ProductCatID, "name": c.ProductCategory} for c in cats]
        verified_data = "\n".join(f"{c.ProductCatID}: {c.ProductCategory}" for c in cats) or "No active categories found."
        if cats:
            names = ", ".join(c.ProductCategory for c in cats)
            template_reply = f"We currently offer these active product categories: {names}."
        else:
            template_reply = "I couldn't find any active product categories in the current CRM database."

    # ---------------- PRODUCT_INFORMATION ----------------
    elif intent == Intent.PRODUCT_INFORMATION:
        hint = extract_product_hint(message)
        product = _find_product(db, hint) if hint else None
        if product:
            status_note = "" if product.PStatus == 1 else " This product is currently marked inactive."
            cat_name = _get_product_category(db, product) or "unspecified category"
            structured_data = {"PID": product.PID, "name": product.ProductName,
                                "category": cat_name, "status": product.PStatus}
            verified_data = f"{product.PID}: {product.ProductName}, category={cat_name}, status={product.PStatus}"
            template_reply = f"{product.ProductName} belongs to {cat_name}.{status_note}"
        else:
            products = db.query(ProductMaster).all()
            structured_data = [
                {"PID": p.PID, "name": p.ProductName,
                 "category": _get_product_category(db, p),
                 "status": p.PStatus}
                for p in products
            ]
            verified_data = "\n".join(f"{p.PID}: {p.ProductName} ({p.PStatus})" for p in products) or "No products found."
            if products:
                lines = "\n".join(f"- {p.ProductName}{'' if p.PStatus == 1 else ' — inactive'}"
                                   for p in products)
                template_reply = f"Here are our available products:\n\n{lines}"
            else:
                template_reply = "I couldn't find any products in the current CRM database."

    # ---------------- IRON_ORE_SPECIFICATION ----------------
    elif intent == Intent.IRON_ORE_SPECIFICATION:
        hint = extract_product_hint(message)
        product = _find_product(db, hint) if hint else None
        lot = extract_lot_hint(message)
        parameter = extract_parameter_hint(message)

        q = db.query(IronOreSpecificationMaster)
        if product:
            # Try to convert product PID to int for spec table comparison
            try:
                pid_int = int(product.PID)
                q = q.filter(IronOreSpecificationMaster.PID == pid_int)
            except (ValueError, TypeError):
                # Product PID is not numeric, can't match
                pass
        if lot:
            q = q.filter(IronOreSpecificationMaster.LotNo == lot)
        if parameter:
            q = q.filter(IronOreSpecificationMaster.Parameter.ilike(f"%{parameter}%"))
        rows = q.all()

        structured_data = [{"parameter": r.Parameter, "specification": r.Specification,
                             "lotNo": r.LotNo} for r in rows]
        table_md = _spec_table_markdown(rows, include_testing_standard=False)
        verified_data = table_md
        if rows:
            product_label = f" for {product.ProductName} (ID: {product.PID})" if product else ""
            template_reply = f"I found the Iron Ore specifications{product_label}. These define the chemical composition and quality parameters for this product:\n\n{table_md}"
        elif product:
            template_reply = (
                f"I couldn't find the requested specification for {product.ProductName} "
                f"(ID: {product.PID}) in the current CRM database."
            )
        else:
            template_reply = (
                "I couldn't find matching Iron Ore specifications. Could you tell me the "
                "product name or ID (e.g. P001) you'd like specifications for?"
            )

    # ---------------- IRON_PELLET_SPECIFICATION ----------------
    elif intent == Intent.IRON_PELLET_SPECIFICATION:
        hint = extract_product_hint(message)
        product = _find_product(db, hint) if hint else None
        parameter = extract_parameter_hint(message)

        q = db.query(IronPelletSpecificationMaster)
        if product:
            # Try to convert product PID to int for spec table comparison
            try:
                pid_int = int(product.PID)
                q = q.filter(IronPelletSpecificationMaster.PID == pid_int)
            except (ValueError, TypeError):
                # Product PID is not numeric, can't match
                pass
        if parameter:
            q = q.filter(IronPelletSpecificationMaster.Parameter.ilike(f"%{parameter}%"))
        rows = q.all()

        structured_data = [{"parameter": r.Parameter, "specification": r.Specification,
                             "testingStandard": r.TestingStandard} for r in rows]
        table_md = _spec_table_markdown(rows, include_testing_standard=True)
        verified_data = table_md
        if rows:
            product_label = f" for {product.ProductName} (ID: {product.PID})" if product else ""
            template_reply = f"I found the Iron Pellet specifications{product_label}. Here are the key quality parameters and testing standards:\n\n{table_md}"
        elif product:
            template_reply = (
                f"I couldn't find the requested specification for {product.ProductName} "
                f"(ID: {product.PID}) in the current CRM database."
            )
        else:
            template_reply = (
                "I couldn't find matching Iron Pellet specifications. Could you tell me the "
                "product name or ID (e.g. P003) you'd like specifications for?"
            )

    # ---------------- INVENTORY_CHECK ----------------
    elif intent == Intent.INVENTORY_CHECK:
        hint = extract_product_hint(message)
        product = _find_product(db, hint) if hint else None
        if product:
            verified_data = f"Product status for {product.PID}: {product.PStatus}. No inventory quantity table exists."
            template_reply = (
                f"{product.ProductName} (ID: {product.PID}) is currently marked "
                f"'{product.PStatus}'. I can confirm the product status from the current "
                f"database, but exact available quantity is not available in the connected "
                f"database yet."
            )
        else:
            verified_data = "No inventory quantity table exists."
            template_reply = (
                "I can confirm a product's active/inactive status from our database, but "
                "current inventory quantity is not available in the connected database. "
                "Could you tell me which product you're asking about?"
            )

    # ---------------- QUOTATION_REQUEST ----------------
    elif intent == Intent.QUOTATION_REQUEST:
        # Handle product selection (select_product_quotation:INDEX)
        if payload.action and payload.action.startswith("select_product_quotation:"):
            product_index = payload.action.replace("select_product_quotation:", "").strip()
            
            try:
                index = int(product_index)
                
                # Get available products again
                all_products = db.query(ProductMaster).all()
                available_products = []
                
                for product in all_products:
                    produced = db.query(func.sum(InventoryMaster.QuantityMT)).filter(
                        InventoryMaster.PID == product.PID,
                        InventoryMaster.Category == 'Produced'
                    ).scalar() or 0
                    
                    sold = db.query(func.sum(InventoryMaster.QuantityMT)).filter(
                        InventoryMaster.PID == product.PID,
                        InventoryMaster.Category == 'Sold'
                    ).scalar() or 0
                    
                    available = float(produced) - float(sold)
                    if available > 0:
                        available_products.append(product)
                
                if index < len(available_products):
                    selected_product = available_products[index]
                    
                    # Calculate available quantity
                    produced = db.query(func.sum(InventoryMaster.QuantityMT)).filter(
                        InventoryMaster.PID == selected_product.PID,
                        InventoryMaster.Category == 'Produced'
                    ).scalar() or 0
                    
                    sold = db.query(func.sum(InventoryMaster.QuantityMT)).filter(
                        InventoryMaster.PID == selected_product.PID,
                        InventoryMaster.Category == 'Sold'
                    ).scalar() or 0
                    
                    available_qty = float(produced) - float(sold)
                    
                    template_reply = (
                        f"Great! You selected **{selected_product.ProductName}**\n\n"
                        f"**Available Stock:** {available_qty:,.2f} MT\n\n"
                        f"Please enter the quantity you need (in MT):\n"
                        f"*Example: 50 or 100.5*"
                    )
                    
                    verified_data = f"Product selected: {selected_product.PID}"
                    structured_data = {
                        "product_id": selected_product.PID,
                        "product_name": selected_product.ProductName,
                        "available_quantity": available_qty,
                        "status": "awaiting_quantity"
                    }
                else:
                    template_reply = "Invalid product selection. Please try again."
                    verified_data = "Invalid product index"
                    structured_data = {}
                    
            except ValueError:
                template_reply = "Invalid selection format. Please try again."
                verified_data = "Invalid product selection format"
                structured_data = {}
        
        # Handle quantity submission (submit_quantity_quotation:PID:QUANTITY)
        elif payload.action and payload.action.startswith("submit_quantity_quotation:"):
            parts = payload.action.split(":")
            if len(parts) >= 3:
                product_pid = parts[1]
                try:
                    requested_quantity = float(parts[2])
                    notes = ":".join(parts[3:]) if len(parts) > 3 else ""
                except (ValueError, IndexError):
                    template_reply = "Invalid quantity. Please enter a valid number."
                    verified_data = "Invalid quantity format"
                    structured_data = {}
                else:
                    if requested_quantity <= 0:
                        template_reply = "Quantity must be greater than 0. Please try again."
                        verified_data = "Invalid quantity: must be > 0"
                        structured_data = {}
                    else:
                        # Find product
                        product = db.query(ProductMaster).filter(ProductMaster.PID == product_pid).first()
                        if not product:
                            template_reply = "Product not found. Please start again."
                            verified_data = f"Product not found: {product_pid}"
                            structured_data = {}
                        else:
                            # Check available quantity
                            produced = db.query(func.sum(InventoryMaster.QuantityMT)).filter(
                                InventoryMaster.PID == product_pid,
                                InventoryMaster.Category == 'Produced'
                            ).scalar() or 0
                            
                            sold = db.query(func.sum(InventoryMaster.QuantityMT)).filter(
                                InventoryMaster.PID == product_pid,
                                InventoryMaster.Category == 'Sold'
                            ).scalar() or 0
                            
                            available_qty = float(produced) - float(sold)
                            
                            if requested_quantity > available_qty:
                                template_reply = (
                                    f"Only {available_qty:,.2f} MT available, but you requested {requested_quantity:,.2f} MT.\n\n"
                                    f"Would you like to order {available_qty:,.2f} MT instead?"
                                )
                                verified_data = f"Insufficient inventory"
                                structured_data = {
                                    "product_id": product_pid,
                                    "requested_quantity": requested_quantity,
                                    "available_quantity": available_qty,
                                    "status": "insufficient_quantity"
                                }
                            else:
                                # Generate quotation
                                try:
                                    from ..quotation_service import (
                                        create_quotation,
                                        get_price_history,
                                        format_quotation_text
                                    )
                                    
                                    # Create quotation
                                    quotation = create_quotation(
                                        db=db,
                                        customer_id=current_user.CID,
                                        product_id=product_pid,
                                        product_name=product.ProductName,
                                        quantity_mt=requested_quantity,
                                        created_by=current_user.User_Id,
                                        validity_days=7,
                                        notes=notes
                                    )
                                    
                                    # Get price history
                                    price_history = get_price_history(db, product_pid, limit=3)
                                    
                                    # Format response
                                    template_reply = format_quotation_text(
                                        quotation_number=quotation.QuotationNumber,
                                        product_name=product.ProductName,
                                        quantity_mt=requested_quantity,
                                        price_per_mt=quotation.PricePerMT,
                                        total_amount=quotation.TotalAmount,
                                        price_history=price_history,
                                        validity_days=7
                                    )
                                    
                                    verified_data = f"Quotation created: {quotation.QuotationNumber}"
                                    structured_data = {
                                        "quotation_id": quotation.QuotationID,
                                        "quotation_number": quotation.QuotationNumber,
                                        "product_id": product_pid,
                                        "quantity_mt": requested_quantity,
                                        "price_per_mt": quotation.PricePerMT,
                                        "total_amount": quotation.TotalAmount,
                                        "pdf_path": quotation.PDFFilePath,
                                        "status": "quotation_generated"
                                    }
                                except Exception as e:
                                    template_reply = f"Error generating quotation: {str(e)}"
                                    verified_data = f"Quotation generation failed"
                                    structured_data = {}
        
        # Initial quotation request - show available products from inventory
        else:
            verified_data = "Quotation system ready"
            
            # Get all products with their inventory information
            all_products = db.query(ProductMaster).all()
            available_products = []
            
            for product in all_products:
                # Calculate available for each product
                produced = db.query(
                    func.sum(InventoryMaster.QuantityMT)
                ).filter(
                    InventoryMaster.PID == product.PID,
                    InventoryMaster.Category == 'Produced'
                ).scalar() or 0
                
                sold = db.query(
                    func.sum(InventoryMaster.QuantityMT)
                ).filter(
                    InventoryMaster.PID == product.PID,
                    InventoryMaster.Category == 'Sold'
                ).scalar() or 0
                
                available = float(produced) - float(sold)
                
                # Include all products with availability info
                if available > 0:
                    available_products.append(product)
            
            user_display = current_user.User_Name or current_user.User_Id
            
            # Send admin notification
            try:
                from . import notification
                from app.database import SessionLocal
                
                db2 = SessionLocal()
                try:
                    notification.create_alert(
                        title="Quotation Request",
                        message=f"Customer '{user_display}' requested a quotation.\n\n"
                               f"User ID: {current_user.User_Id}",
                        requestor_user_id=current_user.User_Id,
                        requestor_name=user_display,
                        db=db2
                    )
                finally:
                    db2.close()
            except Exception as e:
                print(f"Failed to send notification: {e}")
            
            if available_products:
                # Show list of products as buttons (without quantity)
                products_list = "\n".join([
                    f"• {p.ProductName}"
                    for p in available_products
                ])
                
                template_reply = (
                    f"Hello {user_display}, I can help you generate a quotation!\n\n"
                    f"**Available Products:**\n{products_list}\n\n"
                    f"Please click on a product button below to select it."
                )
                
                structured_data = {
                    "products": [
                        {"pid": p.PID, "name": p.ProductName, "id": i}
                        for i, p in enumerate(available_products)
                    ],
                    "status": "awaiting_product_selection"
                }
            else:
                template_reply = (
                    f"Hello {user_display}, I apologize but we don't have any products available "
                    f"for quotation at the moment. Please contact our sales team for assistance."
                )
                structured_data = {}

    # ---------------- ORDER_REQUEST ----------------
    elif intent == Intent.ORDER_REQUEST:
        # Check if this is a quantity validation request (order_quantity:PID:quantity)
        if payload.action and payload.action.startswith("order_quantity:"):
            parts = payload.action.split(":")
            if len(parts) == 3:
                product_pid = parts[1]
                try:
                    requested_quantity = float(parts[2])
                except (ValueError, TypeError):
                    requested_quantity = 0
                
                # Calculate available quantity for this product (Produced - Sold)
                produced = db.query(
                    func.sum(InventoryMaster.QuantityMT)
                ).filter(
                    InventoryMaster.PID == product_pid,
                    InventoryMaster.Category == 'Produced'
                ).scalar() or 0
                
                sold = db.query(
                    func.sum(InventoryMaster.QuantityMT)
                ).filter(
                    InventoryMaster.PID == product_pid,
                    InventoryMaster.Category == 'Sold'
                ).scalar() or 0
                
                available_qty = float(produced) - float(sold)
                
                if available_qty > 0:
                    if requested_quantity <= available_qty:
                        # Quantity is available - create "Sold" entry to deduct from inventory
                        today = datetime.now().date()
                        
                        # Get the product to get price information
                        product = db.query(ProductMaster).filter(ProductMaster.PID == product_pid).first()
                        
                        # Get latest produced entry for this product
                        latest_produced = db.query(InventoryMaster).filter(
                            InventoryMaster.PID == product_pid,
                            InventoryMaster.Category == 'Produced'
                        ).order_by(InventoryMaster.InventoryID.desc()).first()
                        
                        selling_price = latest_produced.SellingPrice if latest_produced else None
                        initial_price = latest_produced.InitialPrice if latest_produced else None
                        
                        # Create "Sold" inventory entry
                        sold_entry = InventoryMaster(
                            PID=product_pid,
                            Category='Sold',
                            QuantityMT=requested_quantity,
                            ProducedDate=today,
                            InitialPrice=initial_price,
                            SellingPrice=selling_price
                        )
                        db.add(sold_entry)
                        db.commit()
                        
                        # Quantity is available
                        remaining = available_qty - requested_quantity
                        verified_data = f"Order accepted for {product_pid}: {requested_quantity} MT sold, {remaining} MT remaining"
                        template_reply = (
                            f"Great! We have {available_qty} MT available.\n\n"
                            f"You requested {requested_quantity} MT - this quantity is available.\n\n"
                            f"Your order has been accepted. A company executive will contact you shortly for price negotiations.\n\n"
                            f"Thank you for your order!"
                        )
                        structured_data = {
                            "order_status": "accepted",
                            "product_pid": product_pid,
                            "requested_quantity": requested_quantity,
                            "available_quantity": available_qty,
                            "remaining_quantity": remaining
                        }
                    else:
                        # Quantity not fully available
                        verified_data = f"Insufficient inventory for {product_pid}: requested {requested_quantity}, available {available_qty}"
                        template_reply = (
                            f"I see that you requested {requested_quantity} MT, but we only have {available_qty} MT available.\n\n"
                            f"Would you like to:\n"
                            f"1. Proceed with {available_qty} MT instead?\n"
                            f"2. Reduce your quantity to what's available?\n"
                            f"3. Wait for restocking (contact our sales team for estimated delivery)?\n\n"
                            f"Please let me know how you'd like to proceed."
                        )
                        structured_data = {
                            "order_status": "insufficient_quantity",
                            "product_pid": product_pid,
                            "requested_quantity": requested_quantity,
                            "available_quantity": available_qty
                        }
                else:
                    # No inventory found
                    verified_data = f"No inventory record for product {product_pid}"
                    template_reply = (
                        f"Unfortunately, this product is currently out of stock.\n\n"
                        f"Please contact our sales team for availability and estimated restocking date."
                    )
                    structured_data = {
                        "order_status": "out_of_stock",
                        "product_pid": product_pid
                    }
        else:
            # Regular order request - show available products
            verified_data = "pending category selection"
            
            # Get personalized greeting
            customer_company = None
            if current_user.CID:
                customer = db.query(CustomerDetail).filter(CustomerDetail.CID == current_user.CID).first()
                if customer:
                    customer_company = customer.CustomerName
            user_display = current_user.User_Name or current_user.User_Id
            if customer_company:
                personalized_greeting = f"{user_display} from {customer_company}"
            else:
                personalized_greeting = user_display
            
            # Fetch products that have available inventory (QuantityMT > 0)
            # Calculate available as (Produced - Sold)
            
            # Get all products
            all_products = db.query(ProductMaster).all()
            available_products = []
            
            for product in all_products:
                # Calculate available for each product
                produced = db.query(
                    func.sum(InventoryMaster.QuantityMT)
                ).filter(
                    InventoryMaster.PID == product.PID,
                    InventoryMaster.Category == 'Produced'
                ).scalar() or 0
                
                sold = db.query(
                    func.sum(InventoryMaster.QuantityMT)
                ).filter(
                    InventoryMaster.PID == product.PID,
                    InventoryMaster.Category == 'Sold'
                ).scalar() or 0
                
                available = float(produced) - float(sold)
                
                # Only include if available
                if available > 0:
                    available_products.append(product)
            
            structured_data = [
                {"PID": p.PID, "name": p.ProductName,
                 "category": _get_product_category(db, p),
                 "status": p.PStatus}
                for p in available_products
            ]
            
            # Send admin notification
            try:
                from . import notification
                from app.database import SessionLocal
                
                db2 = SessionLocal()
                try:
                    notification.create_alert(
                        title="Order Request",
                        message=f"Customer '{user_display}' wants to place an order.\n\n"
                               f"Customer: {personalized_greeting}\n"
                               f"User ID: {current_user.User_Id}",
                        requestor_user_id=current_user.User_Id,
                        requestor_name=user_display,
                        db=db2
                    )
                finally:
                    db2.close()
            except Exception as e:
                print(f"Failed to send notification: {e}")
            
            if available_products:
                template_reply = (
                    f"Hello {user_display}, I can help you place an order."
                )
            else:
                template_reply = (
                    f"Hello {user_display}, I apologize but we don't have any products available at the moment. "
                    f"Please contact our sales team for assistance."
                )

    # ---------------- ORDER_TRACKING ----------------
    elif intent == Intent.ORDER_TRACKING:
        verified_data = "Order/Dispatch tables do not exist yet."
        
        # Send admin notification
        try:
            from . import notification
            from app.database import SessionLocal
            
            db2 = SessionLocal()
            try:
                notification.create_alert(
                    title="Order Tracking Request",
                    message=f"Customer '{user_display}' wants to track their order.\n\n"
                           f"Customer: {personalized_greeting}\n"
                           f"User ID: {current_user.User_Id}\n\n"
                           f"Note: Order tracking is not yet available in the database.",
                    requestor_user_id=current_user.User_Id,
                    requestor_name=user_display or current_user.User_Id,
                    db=db2
                )
            finally:
                db2.close()
        except Exception as e:
            print(f"Failed to send notification: {e}")
        
        template_reply = (
            f"Hello {user_display}, I'm sorry but order tracking is not yet available in our database.\n\n"
            f"Our admin team has been notified about your request. Please contact our sales team "
            f"for the status of your order, or use WhatsApp at {get_company_whatsapp()} "
            f"for faster assistance."
        )

    # ---------------- COMPLAINT_TRACKING ----------------
    elif intent == Intent.COMPLAINT_TRACKING:
        from ..intent import extract_complaint_id
        
        # Check if user clicked on a specific complaint from the list
        if payload.action and payload.action.startswith("view_complaint:"):
            complaint_id = payload.action.split(":", 1)[1].strip()
        else:
            # Try to extract complaint ID from message
            complaint_id = extract_complaint_id(message)
        
        if complaint_id:
            # Look up the complaint
            complaint = db.query(ComplaintMaster).filter(
                ComplaintMaster.ComplaintID == complaint_id
            ).first()
            
            if complaint:
                # Check if this complaint belongs to the current user
                if complaint.CreatedBy != current_user.User_Id:
                    overall_status = "Not Found"
                    verified_data = f"Complaint {complaint_id} not found for this user"
                    template_reply = (
                        f"I couldn't find a complaint with ID **{complaint_id}** in your account.\n\n"
                        f"Please verify the complaint ID and try again."
                    )
                else:
                    # Check if ALL workflow columns have data
                    has_root_cause = complaint.RootCauseAnalysis and complaint.RootCauseAnalysis.strip()
                    has_root_cause_date = complaint.RootCauseAnalysisDate
                    has_corrective_action = complaint.CorrectivePreventiveAction and complaint.CorrectivePreventiveAction.strip()
                    has_corrective_date = complaint.CorrectivePreventiveActionDate
                    has_marketing_review = complaint.MarketingReview and complaint.MarketingReview.strip()
                    has_marketing_date = complaint.MarketingReviewDate
                    has_plant_head_review = complaint.PlantHeadReview and complaint.PlantHeadReview.strip()
                    has_plant_head_date = complaint.PlantHeadReviewDate
                    
                    # Check if ANY workflow columns are filled (one or more)
                    any_workflow_filled = (
                        has_root_cause or has_root_cause_date or
                        has_corrective_action or has_corrective_date or
                        has_marketing_review or has_marketing_date or
                        has_plant_head_review or has_plant_head_date
                    )
                    
                    # Check if ALL workflow columns are filled (only then show "will be resolved in 2-3 days")
                    all_workflow_complete = (
                        has_root_cause and has_root_cause_date and
                        has_corrective_action and has_corrective_date and
                        has_marketing_review and has_marketing_date and
                        has_plant_head_review and has_plant_head_date
                    )
                    
                    # Determine status and show only status to customer
                    if complaint.Status == "Resolved":
                        # Status 3: Resolved
                        overall_status = "Resolved"
                        verified_data = f"Complaint {complaint_id} resolved"
                        template_reply = (
                            f"Hello {current_user.User_Name},\n\n"
                            f"**Complaint ID:** {complaint.ComplaintID}\n"
                            f"**Status:** ✅ Resolved\n\n"
                            f"Your complaint has been resolved. Thank you for your patience."
                        )
                    elif all_workflow_complete:
                        # Status 2: Will be resolved in 2-3 working days (ALL workflow fields filled)
                        # Generate and save solution if not already generated
                        if not complaint.Solution or not complaint.Solution.strip():
                            # Generate solution with Ollama
                            verified_data_parts = [
                                f"Complaint Category: {complaint.CategoryType}",
                                f"Customer Issue: {complaint.ComplaintDescription}",
                                f"\nRoot Cause Analysis: {complaint.RootCauseAnalysis}",
                                f"Analyzed On: {complaint.RootCauseAnalysisDate.strftime('%B %d, %Y') if complaint.RootCauseAnalysisDate else 'N/A'}",
                                f"\nCorrective/Preventive Action: {complaint.CorrectivePreventiveAction}",
                                f"Action Date: {complaint.CorrectivePreventiveActionDate.strftime('%B %d, %Y') if complaint.CorrectivePreventiveActionDate else 'N/A'}",
                                f"\nMarketing Review: {complaint.MarketingReview}",
                                f"Marketing Review Date: {complaint.MarketingReviewDate.strftime('%B %d, %Y') if complaint.MarketingReviewDate else 'N/A'}",
                                f"\nPlant Head Review: {complaint.PlantHeadReview}",
                                f"Plant Head Review Date: {complaint.PlantHeadReviewDate.strftime('%B %d, %Y') if complaint.PlantHeadReviewDate else 'N/A'}",
                            ]
                            
                            verified_data_str = "\n".join(verified_data_parts)
                            
                            # Prompt for Ollama to generate solution
                            customer_message = (
                                "Based on all the investigation data, root cause analysis, corrective actions taken, "
                                "and all reviews completed, write a warm and professional solution message for the customer. "
                                "Explain in simple human language what was the problem, what we found, what we did to fix it, "
                                "and reassure them that the issue is now resolved. Keep it concise and friendly."
                            )
                            
                            # Generate solution with Ollama
                            generated_solution = ollama_client.generate_reply(customer_message, verified_data_str)
                            
                            # Save the generated solution to database
                            if generated_solution:
                                complaint.Solution = generated_solution
                                complaint.UpdatedDate = datetime.now()
                                complaint.UpdatedBy = "System"
                                db.commit()
                        
                        overall_status = "In Progress"
                        verified_data = f"Complaint {complaint_id} in progress - will resolve in 2-3 days"
                        template_reply = (
                            f"Hello {current_user.User_Name},\n\n"
                            f"**Complaint ID:** {complaint.ComplaintID}\n"
                            f"**Status:** ⏳ Will be resolved in 2-3 working days\n\n"
                            f"Our team is finalizing the resolution. Thank you for your patience."
                        )
                    else:
                        # Status 1: Under Review (only category + description, or any workflow fields filled but not all)
                        overall_status = "Under Review"
                        verified_data = f"Complaint {complaint_id} under review"
                        template_reply = (
                            f"Hello {current_user.User_Name},\n\n"
                            f"**Complaint ID:** {complaint.ComplaintID}\n"
                            f"**Status:** 📝 Under Review\n\n"
                            f"Your complaint is being investigated. We will update you shortly."
                        )
                    
                    structured_data = {
                        "complaint_id": complaint.ComplaintID,
                        "category": complaint.CategoryType,
                        "status": overall_status,
                    }
            else:
                overall_status = "Not Found"
                verified_data = f"Complaint {complaint_id} not found"
                template_reply = (
                    f"I couldn't find a complaint with ID **{complaint_id}** in our system.\n\n"
                    f"Please verify the complaint ID and try again, or contact support for assistance."
                )
        else:
            # No complaint ID in action, check if message mentions complaint keywords
            msg_lower = message.lower()
            complaint_keywords = ["complaint", "status", "solution", "issue", "resolved", "review", "track"]
            has_complaint_keywords = any(keyword in msg_lower for keyword in complaint_keywords)
            
            if has_complaint_keywords:
                # User is asking about a complaint, try to find their most recent one
                user_complaints = db.query(ComplaintMaster).filter(
                    ComplaintMaster.CreatedBy == current_user.User_Id
                ).order_by(ComplaintMaster.CreatedDate.desc()).all()
                
                if user_complaints:
                    # Get the most recent complaint
                    recent_complaint = user_complaints[0]
                    
                    # Check workflow data to determine status
                    has_root_cause = recent_complaint.RootCauseAnalysis and recent_complaint.RootCauseAnalysis.strip()
                    has_root_cause_date = recent_complaint.RootCauseAnalysisDate
                    has_corrective_action = recent_complaint.CorrectivePreventiveAction and recent_complaint.CorrectivePreventiveAction.strip()
                    has_corrective_date = recent_complaint.CorrectivePreventiveActionDate
                    has_marketing_review = recent_complaint.MarketingReview and recent_complaint.MarketingReview.strip()
                    has_marketing_date = recent_complaint.MarketingReviewDate
                    has_plant_head_review = recent_complaint.PlantHeadReview and recent_complaint.PlantHeadReview.strip()
                    has_plant_head_date = recent_complaint.PlantHeadReviewDate
                    
                    # Check if ANY workflow columns are filled (one or more)
                    any_workflow_filled = (
                        has_root_cause or has_root_cause_date or
                        has_corrective_action or has_corrective_date or
                        has_marketing_review or has_marketing_date or
                        has_plant_head_review or has_plant_head_date
                    )
                    
                    # Check if ALL workflow columns are filled (only then show "will be resolved in 2-3 days")
                    all_workflow_complete = (
                        has_root_cause and has_root_cause_date and
                        has_corrective_action and has_corrective_date and
                        has_marketing_review and has_marketing_date and
                        has_plant_head_review and has_plant_head_date
                    )
                    
                    # Determine status
                    if recent_complaint.Status == "Resolved":
                        overall_status = "Resolved"
                        template_reply = (
                            f"Hello {current_user.User_Name},\n\n"
                            f"**Complaint ID:** {recent_complaint.ComplaintID}\n"
                            f"**Status:** ✅ Resolved\n\n"
                            f"Your complaint has been resolved. Thank you for your patience."
                        )
                    elif all_workflow_complete:
                        overall_status = "In Progress"
                        
                        # Generate and save solution if not already generated
                        if not recent_complaint.Solution or not recent_complaint.Solution.strip():
                            # Generate solution with Ollama
                            verified_data_parts = [
                                f"Complaint Category: {recent_complaint.CategoryType}",
                                f"Customer Issue: {recent_complaint.ComplaintDescription}",
                                f"\nRoot Cause Analysis: {recent_complaint.RootCauseAnalysis}",
                                f"Analyzed On: {recent_complaint.RootCauseAnalysisDate.strftime('%B %d, %Y') if recent_complaint.RootCauseAnalysisDate else 'N/A'}",
                                f"\nCorrective/Preventive Action: {recent_complaint.CorrectivePreventiveAction}",
                                f"Action Date: {recent_complaint.CorrectivePreventiveActionDate.strftime('%B %d, %Y') if recent_complaint.CorrectivePreventiveActionDate else 'N/A'}",
                                f"\nMarketing Review: {recent_complaint.MarketingReview}",
                                f"Marketing Review Date: {recent_complaint.MarketingReviewDate.strftime('%B %d, %Y') if recent_complaint.MarketingReviewDate else 'N/A'}",
                                f"\nPlant Head Review: {recent_complaint.PlantHeadReview}",
                                f"Plant Head Review Date: {recent_complaint.PlantHeadReviewDate.strftime('%B %d, %Y') if recent_complaint.PlantHeadReviewDate else 'N/A'}",
                            ]
                            
                            verified_data_str = "\n".join(verified_data_parts)
                            
                            # Prompt for Ollama to generate solution
                            customer_message = (
                                "Based on all the investigation data, root cause analysis, corrective actions taken, "
                                "and all reviews completed, write a warm and professional solution message for the customer. "
                                "Explain in simple human language what was the problem, what we found, what we did to fix it, "
                                "and reassure them that the issue is now resolved. Keep it concise and friendly."
                            )
                            
                            # Generate solution with Ollama
                            generated_solution = ollama_client.generate_reply(customer_message, verified_data_str)
                            
                            # Save the generated solution to database
                            if generated_solution:
                                recent_complaint.Solution = generated_solution
                                recent_complaint.UpdatedDate = datetime.now()
                                recent_complaint.UpdatedBy = "System"
                                db.commit()
                        
                        template_reply = (
                            f"Hello {current_user.User_Name},\n\n"
                            f"**Complaint ID:** {recent_complaint.ComplaintID}\n"
                            f"**Status:** ⏳ Will be resolved in 2-3 working days\n\n"
                            f"Our team is finalizing the resolution. Thank you for your patience."
                        )
                    else:
                        overall_status = "Under Review"
                        template_reply = (
                            f"Hello {current_user.User_Name},\n\n"
                            f"**Complaint ID:** {recent_complaint.ComplaintID}\n"
                            f"**Status:** 📝 Under Review\n\n"
                            f"Your complaint is being investigated. We will update you shortly."
                        )
                    
                    verified_data = f"Complaint {recent_complaint.ComplaintID} status check"
                    structured_data = {
                        "complaint_id": recent_complaint.ComplaintID,
                        "category": recent_complaint.CategoryType,
                        "status": overall_status,
                    }
                else:
                    # No complaints found
                    verified_data = "No complaints found for this user"
                    template_reply = (
                        f"Hello {current_user.User_Name}, I couldn't find any complaints in your account.\n\n"
                        f"If you'd like to raise a new complaint, please let me know."
                    )
            else:
                # User not asking about complaints, show list of all complaints for reference
                user_complaints = db.query(ComplaintMaster).filter(
                    ComplaintMaster.CreatedBy == current_user.User_Id
                ).order_by(ComplaintMaster.CreatedDate.desc()).all()
                
                if user_complaints:
                    verified_data = f"User has {len(user_complaints)} complaint(s)"
                    
                    # Build complaint list with clickable options
                    complaint_list = []
                    for c in user_complaints:
                        # Determine status based on Status column or workflow columns
                        status_text = c.Status if c.Status else "Under Review"
                        status_emoji = "✅" if c.Status == "Resolved" else "📝"
                        complaint_list.append(
                            f"{status_emoji} **{c.ComplaintID}**\n"
                            f"   Category: {c.CategoryType or 'General'}\n"
                            f"   Status: {status_text}\n"
                            f"   Date: {c.CreatedDate.strftime('%B %d, %Y') if c.CreatedDate else 'N/A'}"
                        )
                    
                    template_reply = (
                        f"Hello {current_user.User_Name}, here are your registered complaints:\n\n" +
                        "\n\n".join(complaint_list) +
                        "\n\n**Click on a complaint ID above to view its full details.**"
                    )
                    
                    # Add suggested actions with complaint IDs
                    suggested_actions = [f"view_complaint:{c.ComplaintID}" for c in user_complaints[:5]]
                    structured_data = {"suggested_actions": suggested_actions}
                else:
                    verified_data = "No registered complaints found for this user."
                    template_reply = (
                        f"Hello {current_user.User_Name}, I couldn't find any registered complaints for your account.\n\n"
                        f"If you'd like to raise a new complaint, please click 'Raise a Complaint'."
                    )

    # ---------------- COMPLAINT ----------------
    elif intent == Intent.COMPLAINT:
        # Extract complaint details from message
        hint = extract_product_hint(message)
        lot = extract_lot_hint(message)
        
        # Check if complaint category was provided via payload (new flow)
        complaint_category = None
        if payload.action and payload.action.startswith("complaint_category:"):
            complaint_category = payload.action.split(":", 1)[1].strip()
        
        # Check if full complaint data was provided via payload
        complaint_data = None
        if payload.action and "complaint_details" in payload.action:
            try:
                import json
                complaint_data = json.loads(payload.action)
            except:
                pass
        
        if complaint_data:
            # Store the complaint
            complaint_id = f"CMP-{date.today().strftime('%Y%m%d')}-{db.query(ComplaintMaster).filter(ComplaintMaster.CreatedDate >= date.today()).count() + 1:04d}"
            complaint = ComplaintMaster(
                ComplaintID=complaint_id,
                CategoryType=complaint_data.get("category", "General"),
                ComplaintDescription=complaint_data.get("description", ""),
                PONumber=complaint_data.get("po_number"),
                DispatchDate=complaint_data.get("dispatch_date"),
                CreatedBy=current_user.User_Id,
                CreatedDate=datetime.now(),
                Status="Under Review"
            )
            db.add(complaint)
            db.commit()
            
            structured_data = {"complaint_id": complaint_id}
            verified_data = f"Complaint ID: {complaint_id}"
            template_reply = (
                f"Thank you for reporting this issue, {current_user.User_Name}. "
                f"Your complaint has been registered with tracking number **{complaint_id}**.\n\n"
                f"We will investigate the issue and keep you updated on the resolution.\n\n"
                f"If you need to reference this complaint, please use the ID: {complaint_id}"
            )
        elif complaint_category:
            # Category selected, ask for PO number, dispatch date, and description
            verified_data = f"Complaint category {complaint_category} selected, awaiting details"
            template_reply = (
                f"You have selected: **{complaint_category}**\n\n"
                f"Please provide the following details to register your complaint:\n\n"
                f"1. **PO Number**\n"
                f"2. **Dispatch Date**\n"
                f"3. **Complaint Description**\n\n"
                f"You can respond with this information and I'll register your complaint."
            )
        else:
            # Check if message explicitly mentions "new" complaint or "raise" complaint
            # If so, skip the existing complaints check and go straight to category selection
            msg_lower = message.lower()
            wants_new_complaint = any(phrase in msg_lower for phrase in [
                "raise a new", "new complaint", "raise complaint", "file complaint", 
                "register complaint", "create complaint", "submit complaint"
            ])
            
            if not wants_new_complaint:
                # Check if user has previous complaints
                previous_complaints = db.query(ComplaintMaster).filter(
                    ComplaintMaster.CreatedBy == current_user.User_Id
                ).order_by(ComplaintMaster.CreatedDate.desc()).limit(3).all()
                
                if previous_complaints:
                    # User has previous complaints, ask if they want to track one or raise new
                    verified_data = "Complaint pending - has previous complaints"
                    complaint_list = "\n".join(
                        f"• **{c.ComplaintID}** - {c.CategoryType} ({c.CreatedDate.strftime('%Y-%m-%d')})"
                        for c in previous_complaints
                    )
                    template_reply = (
                        f"Hello {current_user.User_Name}, I can help you with your complaint request.\n\n"
                        f"You have {len(previous_complaints)} previous complaint(s):\n{complaint_list}\n\n"
                        f"Do you want to:\n"
                        f"1. **Track the status of an existing complaint** (provide the complaint ID)\n"
                        f"2. **Raise a new complaint**"
                    )
                else:
                    # No previous complaints, show category buttons
                    verified_data = "Complaint pending category selection"
                    template_reply = (
                        f"Hello {current_user.User_Name}, I'm sorry to hear you're experiencing an issue.\n\n"
                        f"Please select one of the following complaint categories to proceed:"
                    )
            else:
                # User explicitly wants to raise a new complaint, show category buttons
                verified_data = "Complaint pending category selection"
                template_reply = (
                    f"Hello {current_user.User_Name}, I'm sorry to hear you're experiencing an issue.\n\n"
                    f"Please select one of the following complaint categories to proceed:"
                )

    # ---------------- WHATSAPP_CONTACT ----------------
    elif intent == Intent.WHATSAPP_CONTACT:
        company_email = get_company_email()
        # Get the logged-in customer's name
        customer_name = None
        if current_user.CID:
            customer = db.query(CustomerDetail).filter(CustomerDetail.CID == current_user.CID).first()
            if customer:
                customer_name = customer.CustomerName
        
        # Fallback to user name if no customer record
        if not customer_name:
            customer_name = current_user.User_Name or current_user.User_Id
        
        if company_email:
            structured_data = {"email": company_email, "customerName": customer_name}
            verified_data = f"Email: {company_email}, Customer: {customer_name}"
            # Format email as a mailto link that frontend can render as clickable
            template_reply = f"Hello {customer_name}! You can reach us by email at [**{company_email}**](mailto:{company_email})\n\nClick the email address to send us a message."
        else:
            verified_data = "Email not configured."
            template_reply = "Our email contact isn't configured yet. Please check back soon or ask for human support."

    # ---------------- HUMAN_SUPPORT ----------------
    elif intent == Intent.HUMAN_SUPPORT:
        contacts = []
        company_email = get_company_email()
        company_phone = get_company_phone()
        if company_email:
            contacts.append(f"email at {company_email}")
        if company_phone:
            contacts.append(f"phone at {company_phone}")
        if current_user.ResponsibleSeller:
            contacts.append(f"your account manager, {current_user.ResponsibleSeller}")
        verified_data = "; ".join(contacts) or "No support contact configured."
        if contacts:
            template_reply = f"I can connect you with our team. You can reach {', or '.join(contacts)}."
        else:
            template_reply = (
                "I can share what's available from our records, but a specific support "
                "contact isn't configured yet. Please check back soon or ask for human support."
            )

    # ---------------- GREETING ----------------
    elif intent == Intent.GREETING:
        verified_data = "greeting"
        # Fetch customer company name if CID is linked
        customer_company = None
        if current_user.CID:
            customer = db.query(CustomerDetail).filter(CustomerDetail.CID == current_user.CID).first()
            if customer:
                customer_company = customer.CustomerName
        
        # Build greeting with user name and/or company
        user_display = current_user.User_Name or ""
        if customer_company:
            greeting_prefix = f"Hello {user_display} from {customer_company}" if user_display else f"Hello from {customer_company}"
        elif user_display:
            greeting_prefix = f"Hello {user_display}"
        else:
            greeting_prefix = "Hello"
            
        template_reply = (
            f"{greeting_prefix}! I can help with customer information, "
            f"products, Iron Ore specifications, Iron Pellet specifications, and quotation, "
            f"order, or complaint requests. You can also contact us via email at {get_company_email()}. What would you like to know?"
        )

    # ---------------- UNKNOWN ----------------
    else:
        verified_data = "No matching intent."
        
        # Get customer name for personalization
        customer_company = None
        if current_user.CID:
            customer = db.query(CustomerDetail).filter(CustomerDetail.CID == current_user.CID).first()
            if customer:
                customer_company = customer.CustomerName
        
        user_display = current_user.User_Name or ""
        if customer_company:
            personalized_greeting = f"{user_display} from {customer_company}" if user_display else f"{customer_company}"
        elif user_display:
            personalized_greeting = user_display
        else:
            personalized_greeting = "Customer"
        
        # Send admin notification for unknown intents
        try:
            from . import notification
            from fastapi import FastAPI
            from app.database import SessionLocal
            from app.models import LoginMaster
            
            # Get admin info for notification
            admin = db.query(LoginMaster).filter(LoginMaster.User_Role == "Admin").first()
            admin_name = admin.User_Name if admin else "Admin"
            
            # Create a temporary session to call the notification router
            db2 = SessionLocal()
            try:
                notification_request = notification.create_alert(
                    title="Unknown Customer Query",
                    message=f"User '{user_display}' asked: '{message or payload.action}'\n\n"
                           f"Customer: {personalized_greeting}\n"
                           f"User ID: {current_user.User_Id}\n"
                           f"User Role: {current_user.User_Role or 'N/A'}",
                    requestor_user_id=current_user.User_Id,
                    requestor_name=user_display or current_user.User_Id,
                    db=db2
                )
            finally:
                db2.close()
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
        
        template_reply = (
            f"Dear {personalized_greeting},\n\n"
            f"Thank you for your inquiry. I couldn't find information about this in our database.\n\n"
            f"Our admin team has been notified and will review your request. They may contact you "
            f"for additional details.\n\n"
            f"If you need immediate assistance, please contact us via WhatsApp at "
            f"{get_company_whatsapp() or 'the support number'} or email at "
            f"{get_company_email() or 'support@company.com'}.\n\n"
            f"Best regards,\nCRM Bot Team"
        )

    # Try Ollama for natural phrasing of the verified data; fall back to
    # the template if Ollama is unavailable or errors.
    # Skip Ollama for greetings and pending/interactive flows.
    # COMPLAINT and COMPLAINT_TRACKING are also skipped here: those branches
    # already build the final customer-facing reply themselves (including,
    # for COMPLAINT_TRACKING, their own dedicated Ollama call to phrase the
    # resolution Solution). verified_data for those branches is often just a
    # short internal marker like "Complaint CMP-... resolved" -- re-running
    # Ollama on that marker here would silently replace the real solution
    # text with a generic reply generated from almost no context.
    skip_ollama_intents = (Intent.GREETING, Intent.COMPLAINT, Intent.COMPLAINT_TRACKING, Intent.ORDER_REQUEST, Intent.PRODUCT_INFORMATION, Intent.QUOTATION_REQUEST)
    skip_ollama_phrases = [
        "pending category selection",
        "pending - has previous complaints",
        "awaiting details",
        "user has",  # For complaint list display like "User has 3 complaint(s)"
        "complaint(s)",
        "under review - missing data",  # Skip Ollama for incomplete complaints
        "Order table does not exist yet"  # Skip Ollama for order requests with product list
    ]
    
    should_use_ollama = (
        intent not in skip_ollama_intents and
        not any(phrase in verified_data.lower() for phrase in skip_ollama_phrases)
    )
    
    generated = None
    if should_use_ollama:
        generated = ollama_client.generate_reply(message or payload.action or "", verified_data)

    final_reply = generated or template_reply
    final_reply = _sanitize_reply(final_reply, current_user.CID, db)

    return ChatResponse(
        reply=final_reply,
        intent=intent.value,
        data=structured_data,
        suggested_actions=ALL_ACTIONS,
    )