from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import ComplaintMaster, LoginMaster
from ..schemas import NotificationOut
from ..auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/admin-queries")
def get_admin_queries(
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all admin queries/notifications for the current user."""
    # Get complaints
    complaints = db.query(ComplaintMaster).filter(
        ComplaintMaster.CreatedBy == current_user.User_Id
    ).order_by(ComplaintMaster.CreatedDate.desc()).limit(100).all()
    
    return [
        {
            "notification_id": c.ComplaintID,
            "title": "Complaint",
            "customer": f"{c.CreatedBy} - {c.CategoryType or 'General'}",
            "message": c.ComplaintDescription or '',
            "timestamp": c.CreatedDate.strftime("%Y-%m-%d %H:%M:%S") if c.CreatedDate else '',
        }
        for c in complaints
    ]


@router.post("/admin", response_model=NotificationOut)
def send_admin_notification(
    title: str,
    message: str,
    requestor_user_id: str,
    requestor_name: str,
    db: Session = Depends(get_db),
):
    """Send notification to CRM admins."""
    # Get all admin users
    admin_users = db.query(LoginMaster).filter(
        LoginMaster.User_Role == "Admin"
    ).all()
    
    # For now, we'll just log the notification
    # In production, this would send email/SMS/push notifications
    notification_id = f"NOT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print(f"\n{'='*60}")
    print(f"ADMIN NOTIFICATION: {notification_id}")
    print(f"{'='*60}")
    print(f"Title: {title}")
    print(f"Message: {message}")
    print(f"Requestor: {requestor_name} (ID: {requestor_user_id})")
    print(f"Timestamp: {datetime.now()}")
    print(f"{'='*60}\n")
    
    return NotificationOut(
        notification_id=notification_id,
        title=title,
        message=message,
        status="sent",
    )


@router.post("/alert", response_model=NotificationOut)
def create_alert(
    title: str,
    message: str,
    requestor_user_id: str,
    requestor_name: str,
    db: Session = Depends(get_db),
):
    """Create an alert for admin review."""
    notification_id = f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Log the alert
    print(f"\n{'='*60}")
    print(f"CRITICAL ALERT: {notification_id}")
    print(f"{'='*60}")
    print(f"Title: {title}")
    print(f"Message: {message}")
    print(f"Requestor: {requestor_name} (ID: {requestor_user_id})")
    print(f"Timestamp: {datetime.now()}")
    print(f"{'='*60}\n")
    
    return NotificationOut(
        notification_id=notification_id,
        title=title,
        message=message,
        status="alerted",
    )
